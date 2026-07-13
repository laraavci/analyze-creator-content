#!/usr/bin/env python3
"""Record and validate the completion basis for a source inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from creator_library_common import (
    COMPLETE_BASES_BY_SCOPE,
    COMPLETION_BASES,
    atomic_write_json,
    inventory_completion_errors,
    read_json_object,
    read_jsonl,
    utc_now,
    validate_inventory,
    validate_run,
)


def nonnegative_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Finalize or explicitly mark partial a source inventory."
    )
    parser.add_argument("--directory", required=True)
    parser.add_argument("--status", choices=("complete", "partial"), required=True)
    parser.add_argument("--basis", choices=sorted(COMPLETION_BASES), required=True)
    parser.add_argument("--expected-items", type=nonnegative_integer)
    parser.add_argument("--profile-stated-count", type=nonnegative_integer)
    parser.add_argument("--unresolved-gap-count", type=nonnegative_integer)
    parser.add_argument("--checked-at", default="")
    parser.add_argument("--method", action="append", default=[])
    parser.add_argument("--authenticated", action="store_true")
    args = parser.parse_args()

    directory = Path(args.directory).expanduser().resolve()
    run, run_errors = read_json_object(directory / "run.json")
    inventory, inventory_errors = read_jsonl(directory / "source-inventory.jsonl")
    errors = run_errors + inventory_errors + validate_inventory(inventory)
    if run is not None:
        errors += validate_run(run)
    if errors:
        raise SystemExit("Inventory finalization failed:\n- " + "\n- ".join(errors))
    assert run is not None

    if args.status == "complete":
        if args.expected_items is None:
            errors.append("--expected-items is required when --status complete")
        if args.unresolved_gap_count is None:
            errors.append("--unresolved-gap-count is required when --status complete")
        allowed = COMPLETE_BASES_BY_SCOPE[run["scope_kind"]]
        if args.basis not in allowed:
            errors.append(
                f"basis {args.basis!r} cannot complete scope {run['scope_kind']!r}; "
                "allowed: " + ", ".join(sorted(allowed))
            )
        if args.expected_items is not None and args.expected_items != len(inventory):
            errors.append(
                f"--expected-items {args.expected_items} does not match "
                f"inventory rows {len(inventory)}"
            )
        if args.unresolved_gap_count not in (None, 0):
            errors.append("a complete inventory must have --unresolved-gap-count 0")
        if not inventory:
            errors.append("an empty inventory cannot be complete")
        if args.basis == "known-count-reconciled":
            if args.profile_stated_count is None:
                errors.append(
                    "--profile-stated-count is required for known-count-reconciled"
                )
            elif args.expected_items is not None and (
                args.profile_stated_count != args.expected_items
            ):
                errors.append(
                    "--profile-stated-count must equal --expected-items for "
                    "known-count-reconciled"
                )
    if errors:
        raise SystemExit("Inventory finalization failed:\n- " + "\n- ".join(errors))

    run["inventory_status"] = args.status
    run["inventory_completion_basis"] = args.basis
    if args.expected_items is not None:
        run["expected_item_count"] = args.expected_items
    if args.profile_stated_count is not None:
        run["profile_stated_count"] = args.profile_stated_count
    if args.unresolved_gap_count is not None:
        run["unresolved_gap_count"] = args.unresolved_gap_count
    run["inventory_checked_at"] = args.checked_at.strip() or utc_now()
    run["updated_at"] = utc_now()
    run["authenticated"] = bool(run.get("authenticated") or args.authenticated)
    methods = [str(value).strip() for value in run.get("acquisition_methods", [])]
    methods += [value.strip() for value in args.method if value.strip()]
    run["acquisition_methods"] = list(dict.fromkeys(value for value in methods if value))

    updated_run_errors = validate_run(run)
    if updated_run_errors:
        raise SystemExit(
            "Inventory finalization failed:\n- " + "\n- ".join(updated_run_errors)
        )

    if args.status == "complete":
        completion_errors = inventory_completion_errors(run, len(inventory))
        if completion_errors:
            raise SystemExit(
                "Inventory finalization failed:\n- " + "\n- ".join(completion_errors)
            )

    atomic_write_json(directory / "run.json", run)
    print(
        json.dumps(
            {
                "directory": str(directory),
                "inventory_status": run["inventory_status"],
                "completion_basis": run["inventory_completion_basis"],
                "expected_item_count": run.get("expected_item_count"),
                "inventory_count": len(inventory),
                "unresolved_gap_count": run.get("unresolved_gap_count"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

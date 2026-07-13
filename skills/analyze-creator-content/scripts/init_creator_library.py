#!/usr/bin/env python3
"""Initialize a durable creator-content analysis run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from creator_library_common import (
    SCHEMA_VERSION,
    SCOPE_KINDS,
    atomic_write_json,
    atomic_write_text,
    slugify,
    utc_now,
    valid_http_url,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize a durable creator-content library run."
    )
    parser.add_argument("--creator", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--profile-url", default="")
    parser.add_argument("--scope-kind", choices=sorted(SCOPE_KINDS), required=True)
    parser.add_argument("--scope", default="all requested content")
    parser.add_argument("--relevance-lens", default="")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    creator = args.creator.strip()
    platform = args.platform.strip().lower()
    requested_scope = args.scope.strip()
    if not creator:
        raise SystemExit("--creator must be non-empty")
    if not platform:
        raise SystemExit("--platform must be non-empty")
    if not requested_scope:
        raise SystemExit("--scope must be non-empty")
    if args.profile_url and not valid_http_url(args.profile_url):
        raise SystemExit("--profile-url must be a valid HTTP(S) URL")

    output = Path(args.output).expanduser().resolve()
    if output.exists() and not output.is_dir():
        raise SystemExit(f"Output path exists and is not a directory: {output}")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(
            f"Refusing to initialize non-empty directory: {output}. "
            "Choose a new directory or resume the existing run."
        )
    output.mkdir(parents=True, exist_ok=True)

    now = utc_now()
    run = {
        "schema_version": SCHEMA_VERSION,
        "creator": creator,
        "creator_slug": slugify(creator),
        "platform": platform,
        "profile_url": args.profile_url,
        "scope_kind": args.scope_kind,
        "requested_scope": requested_scope,
        "relevance_lens": args.relevance_lens.strip(),
        "created_at": now,
        "updated_at": now,
        "inventory_status": "pending",
        "inventory_completion_basis": None,
        "inventory_checked_at": None,
        "profile_stated_count": None,
        "expected_item_count": None,
        "unresolved_gap_count": None,
        "authenticated": False,
        "acquisition_methods": [],
        "notes": [],
    }
    atomic_write_json(output / "run.json", run)
    for filename in (
        "source-inventory.jsonl",
        "content-library.jsonl",
        "pattern-library.jsonl",
    ):
        atomic_write_text(output / filename, "")

    print(
        json.dumps(
            {
                "output": str(output),
                "creator": creator,
                "platform": platform,
                "scope_kind": args.scope_kind,
                "files": [
                    "run.json",
                    "source-inventory.jsonl",
                    "content-library.jsonl",
                    "pattern-library.jsonl",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

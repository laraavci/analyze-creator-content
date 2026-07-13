#!/usr/bin/env python3
"""Validate, aggregate, and safely render a creator-content library."""

from __future__ import annotations

import argparse
import csv
import io
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from creator_library_common import (
    ACCESSIBLE_STATUSES,
    atomic_write_json,
    atomic_write_text,
    csv_safe,
    duplicate_values,
    inventory_completion_errors,
    markdown_text,
    nonempty_string,
    read_json_object,
    read_jsonl,
    sorted_counts,
    valid_http_url,
    validate_inventory,
    validate_run,
    word_count,
)


LIBRARY_FIELDS = [
    "source_id",
    "source_url",
    "platform",
    "creator",
    "published_at",
    "media_type",
    "duration_seconds",
    "language",
    "transcription_status",
    "ocr_status",
    "review_basis",
    "is_relevant",
    "exclusion_reason",
    "topic",
    "content_pillar",
    "content_type",
    "format",
    "hook_text",
    "hook_excerpt",
    "hook_type",
    "opening_visual",
    "premise",
    "structure_beats",
    "cta",
    "tone",
    "audience_job",
    "reusable_script_pattern",
    "series_name",
    "proof_device",
    "research_claims",
    "visible_metrics",
    "analyst_inference",
    "confidence",
    "notes",
]
REQUIRED_LIBRARY_FIELDS = {
    "source_id",
    "source_url",
    "platform",
    "creator",
    "media_type",
    "is_relevant",
    "review_basis",
    "confidence",
}
RELEVANT_ANALYSIS_FIELDS = {
    "topic",
    "content_type",
    "format",
    "hook_type",
}
LINKED_FIELDS = ("source_url", "platform", "creator", "media_type")
FORBIDDEN_DURABLE_FIELDS = {
    "cookie",
    "cookies",
    "downloaded_media_path",
    "full_transcript",
    "media_bytes",
    "password",
    "raw_transcript",
    "session",
    "transcript",
}


def validate_library(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        forbidden = sorted(FORBIDDEN_DURABLE_FIELDS.intersection(record))
        if forbidden:
            errors.append(
                f"library row {index} contains forbidden durable fields: "
                + ", ".join(forbidden)
            )
        missing = sorted(field for field in REQUIRED_LIBRARY_FIELDS if field not in record)
        if missing:
            errors.append(f"library row {index} missing: {', '.join(missing)}")
        for field in ("source_id", "source_url", "platform", "creator", "media_type"):
            if field in record and not nonempty_string(record.get(field)):
                errors.append(f"library row {index} {field} must be a non-empty string")
        if "source_url" in record and not valid_http_url(record.get("source_url")):
            errors.append(f"library row {index} source_url must be a valid HTTP(S) URL")

        is_relevant = record.get("is_relevant")
        if not isinstance(is_relevant, bool):
            errors.append(f"library row {index} is_relevant must be true or false")
        confidence = record.get("confidence")
        if confidence not in {"high", "medium", "low"}:
            errors.append(
                f"library row {index} confidence must be high, medium, or low"
            )
        review_basis = record.get("review_basis")
        if not isinstance(review_basis, list) or not review_basis or not all(
            nonempty_string(value) for value in review_basis
        ):
            errors.append(
                f"library row {index} review_basis must be a non-empty list "
                "of non-empty strings"
            )

        if is_relevant is False and not nonempty_string(record.get("exclusion_reason")):
            errors.append(
                f"library row {index} needs exclusion_reason when is_relevant is false"
            )
        if is_relevant is True:
            for field in sorted(RELEVANT_ANALYSIS_FIELDS):
                if not nonempty_string(record.get(field)):
                    errors.append(
                        f"library row {index} {field} must be non-empty when relevant"
                    )
            beats = record.get("structure_beats")
            if not isinstance(beats, list) or not beats or not all(
                nonempty_string(value) for value in beats
            ):
                errors.append(
                    f"library row {index} structure_beats must be a non-empty "
                    "list of non-empty strings when relevant"
                )

        excerpt = record.get("hook_excerpt", "")
        if excerpt is not None and not isinstance(excerpt, str):
            errors.append(f"library row {index} hook_excerpt must be a string")
        elif isinstance(excerpt, str) and word_count(excerpt) > 12:
            errors.append(
                f"library row {index} hook_excerpt exceeds the 12-word limit"
            )

    for field in ("source_id", "source_url"):
        duplicates = duplicate_values(records, field)
        if duplicates:
            errors.append(f"library duplicate {field} values: {', '.join(duplicates)}")
    return errors


def validate_linkage(
    run: dict[str, Any],
    inventory: list[dict[str, Any]],
    library: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    inventory_by_id = {
        str(record.get("source_id", "")).strip(): record for record in inventory
    }
    for index, record in enumerate(inventory, start=1):
        if record.get("creator") != run.get("creator"):
            errors.append(
                f"inventory row {index} creator does not match run.json creator"
            )
        if record.get("platform") != run.get("platform"):
            errors.append(
                f"inventory row {index} platform does not match run.json platform"
            )

    for index, record in enumerate(library, start=1):
        source_id = str(record.get("source_id", "")).strip()
        source = inventory_by_id.get(source_id)
        if source is None:
            continue
        for field in LINKED_FIELDS:
            if record.get(field) != source.get(field):
                errors.append(
                    f"library row {index} {field} does not match inventory "
                    f"for source_id {source_id}"
                )
    return errors


def markdown_counts(title: str, values: dict[str, int]) -> list[str]:
    lines = [f"## {title}", ""]
    if not values:
        return lines + ["No values recorded.", ""]
    lines += ["| Label | Count |", "|---|---:|"]
    lines += [f"| {markdown_text(label)} | {count} |" for label, count in values.items()]
    lines.append("")
    return lines


def build_pattern_playbook(records: list[dict[str, Any]]) -> str:
    relevant = [record for record in records if record.get("is_relevant") is True]
    lines = ["# Pattern Playbook", ""]
    lines += markdown_counts("Content Types", sorted_counts(relevant, "content_type"))
    lines += markdown_counts("Formats", sorted_counts(relevant, "format"))
    lines += markdown_counts("Hook Types", sorted_counts(relevant, "hook_type"))
    lines += markdown_counts("Content Pillars", sorted_counts(relevant, "content_pillar"))
    lines += markdown_counts("Calls To Action", sorted_counts(relevant, "cta"))

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in relevant:
        pattern = str(record.get("reusable_script_pattern", "")).strip()
        if pattern:
            grouped[pattern].append(record)

    lines += ["## Reused Script Patterns", ""]
    repeated = sorted(
        ((pattern, rows) for pattern, rows in grouped.items() if len(rows) >= 2),
        key=lambda item: (-len(item[1]), item[0].casefold()),
    )
    if not repeated:
        lines += ["No script pattern has at least two source examples yet.", ""]
    else:
        for pattern, rows in repeated:
            lines += [
                f"### {markdown_text(pattern)}",
                "",
                f"Frequency: {len(rows)}",
                "",
                "Examples:",
            ]
            for row in sorted(rows, key=lambda value: str(value.get("source_id", "")))[:5]:
                source_id = markdown_text(row.get("source_id", ""))
                source_url = row.get("source_url", "")
                lines.append(f"- {source_id}: <{source_url}>")
            lines.append("")

    one_offs = sum(1 for rows in grouped.values() if len(rows) == 1)
    lines += [
        "## One-Off Pattern Count",
        "",
        str(one_offs),
        "",
        "One-offs remain in the content library but are not promoted as creator systems.",
        "",
    ]
    return "\n".join(lines)


def build_coverage(
    run: dict[str, Any],
    inventory: list[dict[str, Any]],
    library: list[dict[str, Any]],
) -> dict[str, Any]:
    inventory_ids = {str(item.get("source_id", "")).strip() for item in inventory}
    library_ids = {str(item.get("source_id", "")).strip() for item in library}
    missing = sorted(inventory_ids - library_ids)
    extra = sorted(library_ids - inventory_ids)
    unavailable = sorted(
        str(item.get("source_id", "")).strip()
        for item in inventory
        if item.get("status") not in ACCESSIBLE_STATUSES
    )
    completion_reasons = inventory_completion_errors(run, len(inventory))
    inventory_complete = not completion_reasons
    record_complete = bool(inventory) and not missing and not extra and len(inventory) == len(library)
    source_access_complete = bool(inventory) and not unavailable
    overall_complete = inventory_complete and record_complete and source_access_complete
    return {
        "inventory_complete": inventory_complete,
        "inventory_completion_reasons": completion_reasons,
        "record_coverage_complete": record_complete,
        "source_access_complete": source_access_complete,
        "overall_coverage_complete": overall_complete,
        "missing_source_ids": missing,
        "extra_source_ids": extra,
        "unavailable_source_ids": unavailable,
    }


def build_coverage_report(
    run: dict[str, Any],
    inventory: list[dict[str, Any]],
    library: list[dict[str, Any]],
    coverage: dict[str, Any],
) -> str:
    relevant_count = sum(1 for row in library if row.get("is_relevant") is True)
    excluded_count = sum(1 for row in library if row.get("is_relevant") is False)
    yes_no = lambda value: "yes" if value else "no"
    lines = [
        "# Coverage Report",
        "",
        f"Creator: {markdown_text(run.get('creator', ''))}",
        f"Platform: {markdown_text(run.get('platform', ''))}",
        f"Scope kind: {markdown_text(run.get('scope_kind', ''))}",
        f"Requested scope: {markdown_text(run.get('requested_scope', ''))}",
        f"Inventory status: {markdown_text(run.get('inventory_status', ''))}",
        "Inventory completion basis: "
        + markdown_text(run.get("inventory_completion_basis") or "not recorded"),
        f"Inventory checked at: {markdown_text(run.get('inventory_checked_at') or 'not recorded')}",
        f"Profile-stated count: {markdown_text(run.get('profile_stated_count'))}",
        f"Expected in-scope count: {markdown_text(run.get('expected_item_count'))}",
        f"Unresolved gap count: {markdown_text(run.get('unresolved_gap_count'))}",
        f"Inventory rows: {len(inventory)}",
        f"Library rows: {len(library)}",
        f"Relevant rows: {relevant_count}",
        f"Explicitly excluded rows: {excluded_count}",
        "Inventory complete: " + yes_no(coverage["inventory_complete"]),
        "Record coverage complete: " + yes_no(coverage["record_coverage_complete"]),
        "Source access complete: " + yes_no(coverage["source_access_complete"]),
        "Overall coverage complete: " + yes_no(coverage["overall_coverage_complete"]),
        "",
    ]
    lines += markdown_counts("Inventory Status", sorted_counts(inventory, "status"))

    sections = (
        ("Inventory Completion Gaps", coverage["inventory_completion_reasons"]),
        ("Missing From Library", coverage["missing_source_ids"]),
        ("Extra Library IDs", coverage["extra_source_ids"]),
        ("Unavailable Source IDs", coverage["unavailable_source_ids"]),
    )
    for title, values in sections:
        lines += [f"## {title}", ""]
        lines += [f"- {markdown_text(value)}" for value in values] or ["None."]
        lines.append("")
    return "\n".join(lines)


def render_csv(records: list[dict[str, Any]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=LIBRARY_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for record in records:
        writer.writerow({field: csv_safe(record.get(field)) for field in LIBRARY_FIELDS})
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and build a creator-content library."
    )
    parser.add_argument("--directory", required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    directory = Path(args.directory).expanduser().resolve()
    run, run_errors = read_json_object(directory / "run.json")
    inventory, inventory_errors = read_jsonl(directory / "source-inventory.jsonl")
    library, library_errors = read_jsonl(directory / "content-library.jsonl")
    errors = run_errors + inventory_errors + library_errors
    if run is not None:
        errors += validate_run(run)
    errors += validate_inventory(inventory)
    errors += validate_library(library)
    if run is not None:
        errors += validate_linkage(run, inventory, library)
    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))
    assert run is not None

    ordered_library = sorted(
        library,
        key=lambda record: (
            str(record.get("published_at") or ""),
            str(record.get("source_id") or ""),
        ),
        reverse=True,
    )
    coverage = build_coverage(run, inventory, ordered_library)
    relevant = [record for record in ordered_library if record.get("is_relevant") is True]
    summary = {
        "schema_version": 2,
        "creator": run.get("creator"),
        "platform": run.get("platform"),
        **coverage,
        "inventory_count": len(inventory),
        "library_count": len(ordered_library),
        "relevant_count": len(relevant),
        "excluded_count": len(ordered_library) - len(relevant),
        "content_types": sorted_counts(relevant, "content_type"),
        "formats": sorted_counts(relevant, "format"),
        "hook_types": sorted_counts(relevant, "hook_type"),
        "content_pillars": sorted_counts(relevant, "content_pillar"),
        "calls_to_action": sorted_counts(relevant, "cta"),
        "reused_script_patterns": {
            pattern: count
            for pattern, count in sorted_counts(
                relevant, "reusable_script_pattern"
            ).items()
            if count >= 2
        },
    }

    atomic_write_text(directory / "content-library.csv", render_csv(ordered_library))
    atomic_write_json(directory / "library-summary.json", summary)
    atomic_write_text(
        directory / "pattern-playbook.md", build_pattern_playbook(ordered_library)
    )
    atomic_write_text(
        directory / "coverage-report.md",
        build_coverage_report(run, inventory, ordered_library, coverage),
    )

    if not coverage["overall_coverage_complete"] and not args.allow_incomplete:
        raise SystemExit(
            "Library artifacts were built, but overall coverage is incomplete. "
            "Read coverage-report.md, close the gaps, or rerun with "
            "--allow-incomplete for an explicitly partial deliverable."
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

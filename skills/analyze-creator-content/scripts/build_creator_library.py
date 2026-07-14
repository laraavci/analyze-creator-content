#!/usr/bin/env python3
"""Validate, aggregate, and safely render a creator-content library."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any
from urllib.parse import quote

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
    valid_iso_timestamp,
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
    "content_pillar",
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
VISIBLE_COUNT_FIELDS = ("views", "plays", "likes", "comments", "shares", "saves")
VIDEO_MEDIA_TYPES = {"video", "reel", "short", "shorts", "live", "livestream"}
MIN_BREAKOUT_SAMPLE = 5
BREAKOUT_MULTIPLE = 3.0
SCRIPT_PATTERN_PLACEHOLDERS = {
    "n/a",
    "no discernible pattern",
    "no pattern identified",
    "none",
    "not applicable",
    "not recorded",
    "unknown",
}


def reusable_script_pattern(value: Any) -> str:
    pattern = str(value or "").strip()
    if pattern.casefold() in SCRIPT_PATTERN_PLACEHOLDERS:
        return ""
    return pattern


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

        visible_metrics = record.get("visible_metrics")
        if visible_metrics is not None:
            if not isinstance(visible_metrics, dict):
                errors.append(
                    f"library row {index} visible_metrics must be a JSON object"
                )
            else:
                recorded_count = False
                for field in VISIBLE_COUNT_FIELDS:
                    if field not in visible_metrics:
                        continue
                    recorded_count = True
                    value = visible_metrics.get(field)
                    if (
                        not isinstance(value, int)
                        or isinstance(value, bool)
                        or value < 0
                    ):
                        errors.append(
                            f"library row {index} visible_metrics.{field} must be "
                            "a non-negative integer"
                        )
                if recorded_count and not valid_iso_timestamp(
                    visible_metrics.get("checked_at")
                ):
                    errors.append(
                        f"library row {index} visible_metrics.checked_at must be "
                        "an ISO 8601 timestamp with timezone when counts are recorded"
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


def visible_view_metric(record: dict[str, Any]) -> tuple[str, int] | None:
    metrics = record.get("visible_metrics")
    if not isinstance(metrics, dict):
        return None
    for field in ("views", "plays"):
        value = metrics.get(field)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return field, value
    return None


def is_video_media_type(value: Any) -> bool:
    tokens = set(re.split(r"[^a-z0-9]+", str(value).strip().casefold()))
    return bool(tokens.intersection(VIDEO_MEDIA_TYPES))


def format_metric(value: int | float | None) -> str:
    if value is None:
        return "not available"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}"
    return f"{int(value):,}"


def build_performance(
    inventory: list[dict[str, Any]],
    library: list[dict[str, Any]],
) -> dict[str, Any]:
    inventory_by_id = {
        str(record.get("source_id", "")).strip(): record for record in inventory
    }
    accessible_video_ids = {
        source_id
        for source_id, record in inventory_by_id.items()
        if record.get("status") in ACCESSIBLE_STATUSES
        and is_video_media_type(record.get("media_type"))
    }

    captured: list[tuple[dict[str, Any], str, int]] = []
    metric_counts = {"views": 0, "plays": 0}
    for record in library:
        source_id = str(record.get("source_id", "")).strip()
        if source_id not in accessible_video_ids:
            continue
        metric = visible_view_metric(record)
        if metric is None:
            continue
        metric_name, value = metric
        metric_counts[metric_name] += 1
        captured.append((record, metric_name, value))

    comparison_metric: str | None = None
    if captured:
        comparison_metric = max(
            metric_counts,
            key=lambda name: (metric_counts[name], name == "views"),
        )
    comparable = [row for row in captured if row[1] == comparison_metric]
    values = [row[2] for row in comparable]
    median_value = median(values) if values else None
    baseline_eligible = (
        len(values) >= MIN_BREAKOUT_SAMPLE
        and median_value is not None
        and median_value > 0
    )

    ranked: list[dict[str, Any]] = []
    for record, metric_name, value in sorted(
        comparable,
        key=lambda item: (-item[2], str(item[0].get("source_id", ""))),
    ):
        multiple = value / median_value if median_value else None
        is_breakout = bool(
            baseline_eligible
            and multiple is not None
            and multiple >= BREAKOUT_MULTIPLE
        )
        metrics = record.get("visible_metrics", {})
        ranked.append(
            {
                "source_id": record.get("source_id"),
                "source_url": record.get("source_url"),
                "metric": metric_name,
                "visible_count": value,
                "checked_at": metrics.get("checked_at"),
                "published_at": record.get("published_at"),
                "multiple_of_median": (
                    round(multiple, 2) if multiple is not None else None
                ),
                "creator_relative_breakout": is_breakout,
                "signal": (
                    "creator-relative breakout candidate"
                    if is_breakout
                    else "ranked by visible metric only"
                ),
                "content_type": record.get("content_type"),
                "topic": record.get("topic"),
                "hook_text": record.get("hook_text"),
            }
        )

    breakouts = [row for row in ranked if row["creator_relative_breakout"]]
    return {
        "accessible_video_count": len(accessible_video_ids),
        "videos_with_visible_view_or_play_count": len(captured),
        "comparison_metric": comparison_metric,
        "comparable_video_count": len(comparable),
        "alternate_metric_video_count": len(captured) - len(comparable),
        "metric_coverage_ratio": (
            round(len(captured) / len(accessible_video_ids), 4)
            if accessible_video_ids
            else None
        ),
        "median_visible_count": median_value,
        "minimum_breakout_sample": MIN_BREAKOUT_SAMPLE,
        "breakout_multiple_threshold": BREAKOUT_MULTIPLE,
        "breakout_baseline_eligible": baseline_eligible,
        "creator_relative_breakout_count": len(breakouts),
        "creator_relative_breakouts": breakouts,
        "top_videos": ranked[:10],
    }


def build_performance_report(
    run: dict[str, Any], performance: dict[str, Any]
) -> str:
    accessible_count = performance["accessible_video_count"]
    captured_count = performance["videos_with_visible_view_or_play_count"]
    comparison_metric = performance["comparison_metric"]
    comparable_count = performance["comparable_video_count"]
    median_value = performance["median_visible_count"]
    lines = [
        "# Viral And Breakout Video Signals",
        "",
        f"Creator: {markdown_text(run.get('creator', ''))}",
        f"Platform: {markdown_text(run.get('platform', ''))}",
        f"Accessible videos in inventory: {accessible_count}",
        f"Videos with timestamped visible views or plays: {captured_count}",
        "",
        "This report ranks visible performance signals. It does not prove absolute "
        "virality or causation.",
        "",
    ]
    if comparison_metric is None:
        lines += [
            "No timestamped visible views or plays were recorded. Top-video ranking "
            "and breakout inference are unavailable.",
            "",
        ]
        return "\n".join(lines)

    lines += [
        f"Comparison metric: visible {comparison_metric}",
        f"Comparable videos: {comparable_count}",
        f"Median visible {comparison_metric}: {format_metric(median_value)}",
        "Breakout rule: at least "
        f"{MIN_BREAKOUT_SAMPLE} comparable videos and at least "
        f"{BREAKOUT_MULTIPLE:g}x the creator median.",
        "Creator-relative breakout candidates: "
        f"{performance['creator_relative_breakout_count']}",
        "",
    ]
    if performance["alternate_metric_video_count"]:
        lines += [
            f"Excluded from the baseline because they used a different visible "
            f"metric: {performance['alternate_metric_video_count']}",
            "",
        ]
    if not performance["breakout_baseline_eligible"]:
        reason = (
            f"fewer than {MIN_BREAKOUT_SAMPLE} comparable videos"
            if comparable_count < MIN_BREAKOUT_SAMPLE
            else "the creator median is zero"
        )
        lines += [
            f"No breakout labels were assigned because {reason}.",
            "",
        ]

    lines += [
        "## Top Videos By Visible Performance",
        "",
        "| Rank | Source ID | Source | Published | Visible count | Captured at | Multiple of median | Signal | Content type | Hook |",
        "|---:|---|---|---|---:|---|---:|---|---|---|",
    ]
    for rank, row in enumerate(performance["top_videos"], start=1):
        multiple = row["multiple_of_median"]
        multiple_text = f"{multiple:.2f}x" if multiple is not None else "n/a"
        source_id = markdown_text(row.get("source_id", ""))
        source_url = quote(
            str(row.get("source_url", "")), safe=":/?#@!$&'*+,;=%"
        )
        source = f"<{source_url}>"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    source_id,
                    source,
                    markdown_text(row.get("published_at") or "not recorded"),
                    format_metric(row.get("visible_count")),
                    markdown_text(row.get("checked_at") or "not recorded"),
                    multiple_text,
                    markdown_text(row.get("signal", "")),
                    markdown_text(row.get("content_type") or "not recorded"),
                    markdown_text(row.get("hook_text") or "not recorded"),
                ]
            )
            + " |"
        )
    lines += [
        "",
        "## Interpretation Limits",
        "",
        "Account age, post age, paid promotion, collaborations, deletions, metric "
        "visibility, and distribution changes can distort creator-relative comparisons.",
        "A breakout signal identifies an outlier worth studying; it does not show "
        "which hook, topic, or format caused the result.",
        "",
    ]
    return "\n".join(lines)


def build_pattern_playbook(records: list[dict[str, Any]]) -> str:
    relevant = [record for record in records if record.get("is_relevant") is True]
    lines = ["# Pattern Playbook", ""]
    lines += markdown_counts("Content Types", sorted_counts(relevant, "content_type"))
    lines += markdown_counts("Formats", sorted_counts(relevant, "format"))
    lines += markdown_counts("Hook Types", sorted_counts(relevant, "hook_type"))
    lines += markdown_counts("Content Pillars", sorted_counts(relevant, "content_pillar"))
    lines += markdown_counts("Topics", sorted_counts(relevant, "topic"))
    lines += markdown_counts("Calls To Action", sorted_counts(relevant, "cta"))
    lines += markdown_counts("Series Names", sorted_counts(relevant, "series_name"))
    lines += markdown_counts("Proof Devices", sorted_counts(relevant, "proof_device"))
    lines += markdown_counts("Audience Jobs", sorted_counts(relevant, "audience_job"))

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in relevant:
        pattern = reusable_script_pattern(record.get("reusable_script_pattern"))
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
    performance = build_performance(inventory, ordered_library)
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
        "topics": sorted_counts(relevant, "topic"),
        "calls_to_action": sorted_counts(relevant, "cta"),
        "series_names": sorted_counts(relevant, "series_name"),
        "proof_devices": sorted_counts(relevant, "proof_device"),
        "audience_jobs": sorted_counts(relevant, "audience_job"),
        "performance": performance,
        "reused_script_patterns": {
            pattern: count
            for pattern, count in sorted_counts(
                [
                    {"pattern": reusable_script_pattern(record.get("reusable_script_pattern"))}
                    for record in relevant
                ],
                "pattern",
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
    atomic_write_text(
        directory / "performance-report.md",
        build_performance_report(run, performance),
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

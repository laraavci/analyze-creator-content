#!/usr/bin/env python3
"""Shared zero-dependency helpers for creator-content library tools."""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


SCHEMA_VERSION = 2
SCOPE_KINDS = {"full-profile", "supplied-links", "date-range", "sample"}
INVENTORY_STATUSES = {"pending", "partial", "complete"}
SOURCE_STATUSES = {
    "accessible",
    "inaccessible",
    "deleted",
    "private",
    "duplicate",
    "unknown",
}
ACCESSIBLE_STATUSES = {"accessible", "duplicate"}
COMPLETION_BASES = {
    "official-export",
    "official-api-enumerated",
    "platform-enumerated-to-end",
    "known-count-reconciled",
    "user-supplied-set",
    "manual-manifest",
}
COMPLETE_BASES_BY_SCOPE = {
    "full-profile": {
        "official-export",
        "official-api-enumerated",
        "platform-enumerated-to-end",
        "known-count-reconciled",
    },
    "date-range": {
        "official-export",
        "official-api-enumerated",
        "platform-enumerated-to-end",
        "known-count-reconciled",
        "manual-manifest",
    },
    "supplied-links": {"user-supplied-set", "manual-manifest"},
    "sample": {"user-supplied-set", "manual-manifest"},
}
REQUIRED_INVENTORY_FIELDS = {
    "source_id",
    "source_url",
    "platform",
    "creator",
    "media_type",
    "status",
    "discovery_basis",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "creator"


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_http_url(value: Any) -> bool:
    if not nonempty_string(value):
        return False
    if any(character in value for character in "\r\n\t<>"):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def valid_iso_timestamp(value: Any) -> bool:
    if not nonempty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def read_json_object(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, [f"Missing file: {path}"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        return None, [f"Could not read {path.name}: {error}"]
    except json.JSONDecodeError as error:
        return None, [
            f"{path.name}:{error.lineno}:{error.colno}: invalid JSON: "
            f"{error.msg}"
        ]
    if not isinstance(value, dict):
        return None, [f"{path.name}: expected one JSON object"]
    return value, []


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return records, [f"Missing file: {path}"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        return records, [f"Could not read {path.name}: {error}"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(
                f"{path.name}:{line_number}:{error.colno}: invalid JSON: "
                f"{error.msg}"
            )
            continue
        if not isinstance(value, dict):
            errors.append(
                f"{path.name}:{line_number}: expected a JSON object"
            )
            continue
        records.append(value)
    return records, errors


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def duplicate_values(records: Iterable[dict[str, Any]], field: str) -> list[str]:
    values = [str(record.get(field, "")).strip() for record in records]
    counts = Counter(value for value in values if value)
    return sorted(value for value, count in counts.items() if count > 1)


def validate_inventory(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        missing = sorted(field for field in REQUIRED_INVENTORY_FIELDS if field not in record)
        if missing:
            errors.append(f"inventory row {index} missing: {', '.join(missing)}")
        for field in REQUIRED_INVENTORY_FIELDS:
            if field in record and not nonempty_string(record.get(field)):
                errors.append(f"inventory row {index} {field} must be a non-empty string")
        if "source_url" in record and not valid_http_url(record.get("source_url")):
            errors.append(f"inventory row {index} source_url must be a valid HTTP(S) URL")
        status = record.get("status")
        if status is not None and status not in SOURCE_STATUSES:
            errors.append(
                f"inventory row {index} status must be one of: "
                + ", ".join(sorted(SOURCE_STATUSES))
            )

    for field in ("source_id", "source_url"):
        duplicates = duplicate_values(records, field)
        if duplicates:
            errors.append(
                f"inventory duplicate {field} values: {', '.join(duplicates)}"
            )
    return errors


def validate_run(run: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if run.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"run.json schema_version must be {SCHEMA_VERSION}; "
            "initialize a new run or migrate the file"
        )
    for field in ("creator", "platform", "scope_kind", "requested_scope"):
        if not nonempty_string(run.get(field)):
            errors.append(f"run.json {field} must be a non-empty string")
    if run.get("scope_kind") not in SCOPE_KINDS:
        errors.append(
            "run.json scope_kind must be one of: " + ", ".join(sorted(SCOPE_KINDS))
        )
    if run.get("inventory_status") not in INVENTORY_STATUSES:
        errors.append(
            "run.json inventory_status must be pending, partial, or complete"
        )
    profile_url = run.get("profile_url")
    if profile_url not in (None, "") and not valid_http_url(profile_url):
        errors.append("run.json profile_url must be empty or a valid HTTP(S) URL")
    for field in ("created_at", "updated_at"):
        if not valid_iso_timestamp(run.get(field)):
            errors.append(f"run.json {field} must be an ISO 8601 timestamp with timezone")
    checked_at = run.get("inventory_checked_at")
    if checked_at is not None and not valid_iso_timestamp(checked_at):
        errors.append(
            "run.json inventory_checked_at must be null or an ISO 8601 timestamp with timezone"
        )
    basis = run.get("inventory_completion_basis")
    if basis is not None and basis not in COMPLETION_BASES:
        errors.append("run.json inventory_completion_basis is invalid")
    for field in (
        "profile_stated_count",
        "expected_item_count",
        "unresolved_gap_count",
    ):
        value = run.get(field)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            errors.append(f"run.json {field} must be null or a non-negative integer")
    if not isinstance(run.get("authenticated"), bool):
        errors.append("run.json authenticated must be true or false")
    for field in ("acquisition_methods", "notes"):
        value = run.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"run.json {field} must be a list of strings")
    return errors


def inventory_completion_errors(
    run: dict[str, Any], inventory_count: int
) -> list[str]:
    """Return reasons a run cannot truthfully claim inventory completion."""
    errors: list[str] = []
    if run.get("inventory_status") != "complete":
        errors.append("inventory_status is not complete")

    scope_kind = run.get("scope_kind")
    basis = run.get("inventory_completion_basis")
    if basis not in COMPLETION_BASES:
        errors.append("inventory_completion_basis is missing or invalid")
    elif basis not in COMPLETE_BASES_BY_SCOPE.get(scope_kind, set()):
        errors.append(f"completion basis {basis!r} is not valid for {scope_kind!r}")

    expected = run.get("expected_item_count")
    if not isinstance(expected, int) or isinstance(expected, bool) or expected < 0:
        errors.append("expected_item_count must be a non-negative integer")
    elif expected != inventory_count:
        errors.append(
            f"expected_item_count {expected} does not match inventory rows {inventory_count}"
        )
    if inventory_count == 0:
        errors.append("inventory is empty")

    gaps = run.get("unresolved_gap_count")
    if not isinstance(gaps, int) or isinstance(gaps, bool) or gaps < 0:
        errors.append("unresolved_gap_count must be a non-negative integer")
    elif gaps != 0:
        errors.append(f"unresolved_gap_count is {gaps}, not zero")

    if not nonempty_string(run.get("inventory_checked_at")):
        errors.append("inventory_checked_at is missing")

    if basis == "known-count-reconciled":
        stated = run.get("profile_stated_count")
        if not isinstance(stated, int) or isinstance(stated, bool) or stated < 0:
            errors.append(
                "profile_stated_count must be a non-negative integer for known-count-reconciled"
            )
        elif isinstance(expected, int) and expected != stated:
            errors.append(
                "expected_item_count must equal profile_stated_count for known-count-reconciled"
            )
    return errors


def markdown_text(value: Any) -> str:
    text = str(value if value is not None else "")
    text = text.replace("\\", "\\\\")
    text = text.replace("\r", " ").replace("\n", " ")
    text = text.replace("|", "\\|")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text.strip()


def csv_safe(value: Any) -> str:
    if value is None:
        text = ""
    elif isinstance(value, list):
        text = " | ".join(str(item) for item in value)
    elif isinstance(value, dict):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    elif isinstance(value, bool):
        text = "true" if value else "false"
    else:
        text = str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", value, flags=re.UNICODE))


def sorted_counts(records: Iterable[dict[str, Any]], field: str) -> dict[str, int]:
    counter = Counter(
        str(record.get(field, "")).strip()
        for record in records
        if str(record.get(field, "")).strip()
    )
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0].casefold())))

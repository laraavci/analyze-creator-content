#!/usr/bin/env python3
"""Fail closed on common private-data and secret leaks before publication."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "__pycache__", "dist", ".work"}
TEXT_SUFFIXES = {
    "",
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".jsonl",
    ".txt",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
}
FORBIDDEN_DATA_SUFFIXES = {
    ".avi",
    ".db",
    ".har",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".sqlite",
    ".wav",
    ".webm",
    ".zip",
}
IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".webp"}


def private_patterns() -> list[tuple[str, re.Pattern[str]]]:
    fragments = [
        ("absolute macOS user path", "/" + "Users" + "/"),
        ("private vault reference", "private" + "-vault"),
        ("private source-repository reference", "mini" + "-me-system"),
        ("private context filename", "AI_" + "CONTEXT.md"),
        ("Codex memory path", ".codex/" + "memories"),
        ("private owner name", "\\b" + "La" + "ra" + "\\b"),
        ("seed creator handle", "lili" + "vogelsang"),
    ]
    return [(label, re.compile(value, re.IGNORECASE)) for label, value in fragments]


SECRET_PATTERNS = [
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "private key",
        re.compile("-----BEGIN " + "(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "assigned secret",
        re.compile(
            r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token)\b"
            r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"
        ),
    ),
]


def candidate_files() -> list[Path]:
    result: list[Path] = []
    for current, directories, filenames in os.walk(ROOT):
        directories[:] = sorted(value for value in directories if value not in EXCLUDED_DIRS)
        for filename in sorted(filenames):
            path = Path(current) / filename
            if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 2_000_000:
                result.append(path)
    return result


def tracked_generated_files() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--", "dist", ".work", "*.pyc"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def main() -> None:
    findings: list[str] = []
    patterns = private_patterns() + SECRET_PATTERNS
    for current, directories, filenames in os.walk(ROOT):
        directories[:] = sorted(value for value in directories if value not in EXCLUDED_DIRS)
        for name in [*directories, *filenames]:
            path = Path(current) / name
            relative = path.relative_to(ROOT)
            if path.is_symlink():
                findings.append(f"{relative}: symbolic links are not allowed")
            suffix = path.suffix.lower()
            if path.is_file() and suffix in FORBIDDEN_DATA_SUFFIXES:
                findings.append(f"{relative}: media, archive, or account-data file is not allowed")
            if (
                path.is_file()
                and suffix in IMAGE_SUFFIXES
                and "assets" not in relative.parts
            ):
                findings.append(
                    f"{relative}: images are allowed only in an explicit assets directory"
                )
    for path in candidate_files():
        relative = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in patterns:
                if pattern.search(line):
                    findings.append(f"{relative}:{line_number}: {label}")
    for path in tracked_generated_files():
        findings.append(f"{path}: generated artifact is tracked")
    for env_name in (".env", ".env.local", ".env.production"):
        if (ROOT / env_name).exists():
            findings.append(f"{env_name}: environment file must not be published")

    if findings:
        raise SystemExit("Public repository audit failed:\n- " + "\n- ".join(findings))
    print(f"Public repository audit passed across {len(candidate_files())} text files.")


if __name__ == "__main__":
    main()

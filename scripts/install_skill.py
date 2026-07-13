#!/usr/bin/env python3
"""Install the canonical skill for Codex, Claude Code, or another client."""

from __future__ import annotations

import argparse
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "analyze-creator-content"
SOURCE = ROOT / "skills" / SKILL_NAME


def skill_root(args: argparse.Namespace) -> Path:
    if args.client == "generic":
        if not args.target:
            raise SystemExit("--target is required for --client generic")
        if args.scope != "user" or args.project:
            raise SystemExit(
                "--scope and --project are not used for --client generic; "
                "pass the skills root with --target"
            )
        return Path(args.target).expanduser().resolve()
    if args.target:
        raise SystemExit("--target is only valid for --client generic")
    folder = ".agents" if args.client == "codex" else ".claude"
    if args.scope == "project":
        if not args.project:
            raise SystemExit("--project is required for --scope project")
        project = Path(args.project).expanduser().resolve()
        if not project.is_dir():
            raise SystemExit(f"Project directory does not exist: {project}")
        return project / folder / "skills"
    if args.project:
        raise SystemExit("--project is only valid for --scope project")
    return Path.home() / folder / "skills"


def verify_source() -> None:
    if not (SOURCE / "SKILL.md").is_file():
        raise SystemExit(f"Canonical skill source is missing: {SOURCE}")
    for path in SOURCE.rglob("*"):
        if path.is_symlink():
            raise SystemExit(f"Refusing to install symlink: {path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Analyze Creator Content.")
    parser.add_argument("--client", choices=("codex", "claude", "generic"), required=True)
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project")
    parser.add_argument("--target")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    verify_source()
    root = skill_root(args)
    destination = root / SKILL_NAME
    if SOURCE.resolve() == destination.resolve():
        raise SystemExit("Source and installation destination are the same directory")
    root.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not args.replace:
        raise SystemExit(
            f"Refusing to overwrite existing skill: {destination}. "
            "Use --replace to create a backup and reinstall."
        )

    backup: Path | None = None
    if destination.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = root / f"{SKILL_NAME}.backup-{stamp}"
        counter = 1
        while backup.exists():
            backup = root / f"{SKILL_NAME}.backup-{stamp}-{counter}"
            counter += 1
        destination.rename(backup)

    temporary = root / f".{SKILL_NAME}.install-{uuid.uuid4().hex}"
    try:
        shutil.copytree(
            SOURCE,
            temporary,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        if not (temporary / "SKILL.md").is_file():
            raise RuntimeError("copied skill is missing SKILL.md")
        os.replace(temporary, destination)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        if backup is not None and backup.exists() and not destination.exists():
            backup.rename(destination)
        raise

    print(f"Installed {SKILL_NAME} to {destination}")
    if backup is not None:
        print(f"Previous installation backed up to {backup}")


if __name__ == "__main__":
    main()

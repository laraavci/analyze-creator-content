#!/usr/bin/env python3
"""Create a reproducible, client-portable skill ZIP and checksum."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "analyze-creator-content"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
DIST = ROOT / "dist"
FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def source_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(SKILL_DIR.rglob("*")):
        if "__pycache__" in path.parts or path.name == ".DS_Store":
            continue
        if path.is_symlink():
            raise SystemExit(f"Refusing to package symlink: {path.relative_to(ROOT)}")
        if path.is_file():
            files.append(path)
    if not files or not (SKILL_DIR / "SKILL.md").exists():
        raise SystemExit("Canonical skill folder is missing or empty")
    return files


def main() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_skill.py")],
        cwd=ROOT,
        check=True,
    )
    DIST.mkdir(parents=True, exist_ok=True)
    archive = DIST / f"{SKILL_NAME}.zip"
    descriptor, temporary_name = tempfile.mkstemp(dir=DIST, suffix=".zip.tmp")
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED) as bundle:
            for path in source_files():
                relative = path.relative_to(SKILL_DIR)
                archive_name = (Path(SKILL_NAME) / relative).as_posix()
                info = zipfile.ZipInfo(archive_name, FIXED_TIMESTAMP)
                info.compress_type = zipfile.ZIP_STORED
                info.external_attr = (0o100644 & 0xFFFF) << 16
                bundle.writestr(info, path.read_bytes())
        os.replace(temporary, archive)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = DIST / f"{SKILL_NAME}.zip.sha256"
    checksum_temporary = DIST / f".{checksum.name}.tmp"
    checksum_temporary.write_text(
        f"{digest}  {archive.name}\n", encoding="utf-8"
    )
    os.replace(checksum_temporary, checksum)
    print(f"Created {archive.relative_to(ROOT)}")
    print(f"SHA-256 {digest}")


if __name__ == "__main__":
    main()

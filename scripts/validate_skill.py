#!/usr/bin/env python3
"""Validate the canonical Agent Skills folder without third-party packages."""

from __future__ import annotations

import py_compile
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "analyze-creator-content"
SKILL_FILE = SKILL_DIR / "SKILL.md"


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["SKILL.md must begin with YAML frontmatter delimited by ---"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["SKILL.md frontmatter is missing its closing ---"]
    values: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"SKILL.md:{line_number}: unsupported frontmatter line")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or not value:
            errors.append(f"SKILL.md:{line_number}: frontmatter keys need values")
            continue
        if key in values:
            errors.append(f"SKILL.md:{line_number}: duplicate frontmatter key {key}")
        values[key] = value
    return values, errors


def main() -> None:
    errors: list[str] = []
    if not SKILL_FILE.exists():
        raise SystemExit(f"Missing canonical skill: {SKILL_FILE}")
    text = SKILL_FILE.read_text(encoding="utf-8")
    frontmatter, frontmatter_errors = parse_frontmatter(text)
    errors += frontmatter_errors

    allowed_frontmatter = {"name", "description", "license", "allowed-tools", "metadata"}
    unexpected = sorted(set(frontmatter) - allowed_frontmatter)
    if unexpected:
        errors.append(
            "unexpected SKILL.md frontmatter keys: " + ", ".join(unexpected)
        )

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("frontmatter name must use lowercase letters, digits, and hyphens")
    if len(name) > 64:
        errors.append("frontmatter name must be at most 64 characters")
    if name != SKILL_DIR.name:
        errors.append("frontmatter name must match the skill directory name")
    if not description:
        errors.append("frontmatter description is required")
    elif len(description) > 1024:
        errors.append("frontmatter description must be at most 1024 characters")
    if "<" in description or ">" in description:
        errors.append("frontmatter description cannot contain angle brackets")
    if "use" not in description.casefold():
        errors.append("frontmatter description should explain when to use the skill")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md must remain under 500 lines; move detail into references")

    placeholder_pattern = re.compile(r"\b(?:TODO|FIXME|TBD)\b|\[TODO", re.IGNORECASE)
    for path in sorted(SKILL_DIR.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"unexpected non-text skill file: {path.relative_to(ROOT)}")
            continue
        if placeholder_pattern.search(content):
            errors.append(f"placeholder remains in {path.relative_to(ROOT)}")

    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for match in link_pattern.finditer(text):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        referenced = (SKILL_DIR / target).resolve()
        try:
            referenced.relative_to(SKILL_DIR.resolve())
        except ValueError:
            errors.append(f"SKILL.md reference escapes the skill directory: {target}")
            continue
        if not referenced.exists():
            errors.append(f"SKILL.md reference does not exist: {target}")

    with tempfile.TemporaryDirectory() as bytecode_directory:
        for index, script in enumerate(
            sorted((SKILL_DIR / "scripts").glob("*.py")), start=1
        ):
            try:
                py_compile.compile(
                    str(script),
                    cfile=str(Path(bytecode_directory) / f"{index}.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as error:
                errors.append(f"Python syntax error in {script.name}: {error.msg}")

    metadata = SKILL_DIR / "agents" / "openai.yaml"
    if metadata.exists():
        metadata_text = metadata.read_text(encoding="utf-8")
        if "$analyze-creator-content" not in metadata_text:
            errors.append("agents/openai.yaml default prompt must invoke the canonical skill")

    if errors:
        raise SystemExit("Skill validation failed:\n- " + "\n- ".join(errors))
    print(
        f"Validated {SKILL_DIR.relative_to(ROOT)}: frontmatter, references, "
        f"{len(list((SKILL_DIR / 'scripts').glob('*.py')))} Python scripts, "
        f"{len(text.splitlines())} SKILL.md lines."
    )


if __name__ == "__main__":
    main()

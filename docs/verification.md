# Verification

Run from the repository root with Python 3.10 or newer.

## Required Before Commit

```bash
python3 scripts/validate_skill.py
python3 -m unittest discover -s tests -v
python3 scripts/package_skill.py
python3 scripts/audit_public_repo.py
git diff --check
```

## What Each Check Proves

- `validate_skill.py`: Agent Skills frontmatter, directory naming, referenced resources, Python syntax, and absence of placeholders.
- unit tests: initialization, safe overwrite behavior, inventory finalization, coverage truth, source linkage, schema and metric validation, creator-relative breakout rules, output safety, packaging, and installation.
- `package_skill.py`: deterministic downloadable ZIP and SHA-256 checksum.
- `audit_public_repo.py`: no known private paths, private source-repository references, common secret patterns, or committed generated artifacts.
- `git diff --check`: no whitespace errors.

## Manual Skill Evals

Use the prompts and scoring rules in `evals/manual-evals.md` with at least one Codex run and one Claude Code run before a tagged release.

## Live Pilot Gate

Before the first release, test an authorized public creator with a small but non-trivial source set. Confirm manually:

1. The inventory completion basis is defensible.
2. Every accessible inventoried item has a library row.
3. Inaccessible items remain visible.
4. Repeated patterns link to two or more sources.
5. No full transcript or downloaded media appears in the durable output.
6. The coverage report does not claim more than the acquisition method proves.
7. Visible performance counts include capture timestamps and one comparable metric.
8. The performance report labels no breakout without the five-video, 3x-median rule.

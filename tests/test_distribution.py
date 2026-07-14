from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.audit_public_repo import missing_local_links


ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "scripts" / "validate_skill.py"
AUDIT = ROOT / "scripts" / "audit_public_repo.py"
PACKAGE = ROOT / "scripts" / "package_skill.py"
INSTALL = ROOT / "scripts" / "install_skill.py"


def run_script(
    script: Path,
    *arguments: object,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(str(value) for value in arguments)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
    )


class DistributionTests(unittest.TestCase):
    def test_public_audit_checks_outer_target_of_badge_links(self) -> None:
        readme = ROOT / "README.md"
        self.assertEqual(
            missing_local_links(
                readme,
                "[![license](https://example.test/license.svg)](LICENSE)",
            ),
            [],
        )
        self.assertEqual(
            missing_local_links(
                readme,
                "[![license](https://example.test/license.svg)](missing-license.txt)",
            ),
            ["missing local link: missing-license.txt"],
        )

    def test_skill_validator_and_public_audit_pass(self) -> None:
        validated = run_script(VALIDATE)
        self.assertEqual(validated.returncode, 0, validated.stderr)
        skill_directory = ROOT / "skills" / "analyze-creator-content"
        self.assertFalse(any(skill_directory.rglob("__pycache__")))
        self.assertFalse(any(skill_directory.rglob("*.pyc")))
        audited = run_script(AUDIT)
        self.assertEqual(audited.returncode, 0, audited.stderr)

    def test_package_is_reproducible_and_has_portable_root(self) -> None:
        first = run_script(PACKAGE)
        self.assertEqual(first.returncode, 0, first.stderr)
        archive = ROOT / "dist" / "analyze-creator-content.zip"
        first_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        second = run_script(PACKAGE)
        self.assertEqual(second.returncode, 0, second.stderr)
        second_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(first_digest, second_digest)
        checksum = (ROOT / "dist" / "analyze-creator-content.zip.sha256").read_text()
        self.assertEqual(checksum, f"{second_digest}  analyze-creator-content.zip\n")
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
        self.assertEqual(names, sorted(names))
        self.assertIn("analyze-creator-content/SKILL.md", names)
        self.assertTrue(all(name.startswith("analyze-creator-content/") for name in names))
        self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))

    def test_packaged_skill_runs_from_extracted_zip(self) -> None:
        packaged = run_script(PACKAGE)
        self.assertEqual(packaged.returncode, 0, packaged.stderr)
        archive = ROOT / "dist" / "analyze-creator-content.zip"
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(base)
            scripts = base / "analyze-creator-content" / "scripts"
            run_directory = base / "smoke-run"
            initialized = run_script(
                scripts / "init_creator_library.py",
                "--creator",
                "archive-smoke",
                "--platform",
                "example",
                "--profile-url",
                "https://example.test/archive-smoke",
                "--scope-kind",
                "supplied-links",
                "--scope",
                "one synthetic video",
                "--output",
                run_directory,
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            inventory = {
                "source_id": "one",
                "source_url": "https://example.test/posts/one",
                "platform": "example",
                "creator": "archive-smoke",
                "media_type": "video",
                "status": "accessible",
                "discovery_basis": "archive smoke fixture",
            }
            library = {
                "source_id": "one",
                "source_url": "https://example.test/posts/one",
                "platform": "example",
                "creator": "archive-smoke",
                "media_type": "video",
                "review_basis": ["synthetic fixture"],
                "is_relevant": True,
                "confidence": "high",
                "topic": "archive smoke",
                "content_pillar": "distribution verification",
                "content_type": "educational explainer",
                "format": "talking head",
                "hook_type": "direct question",
                "structure_beats": ["hook", "payoff"],
                "visible_metrics": {
                    "views": 100,
                    "checked_at": "2026-07-14T12:00:00Z",
                },
            }
            (run_directory / "source-inventory.jsonl").write_text(
                json.dumps(inventory) + "\n", encoding="utf-8"
            )
            (run_directory / "content-library.jsonl").write_text(
                json.dumps(library) + "\n", encoding="utf-8"
            )
            finalized = run_script(
                scripts / "finalize_inventory.py",
                "--directory",
                run_directory,
                "--status",
                "complete",
                "--basis",
                "user-supplied-set",
                "--expected-items",
                1,
                "--unresolved-gap-count",
                0,
                "--method",
                "archive smoke fixture",
            )
            self.assertEqual(finalized.returncode, 0, finalized.stderr)
            built = run_script(
                scripts / "build_creator_library.py", "--directory", run_directory
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertTrue((run_directory / "performance-report.md").is_file())
            self.assertIn(
                "fewer than 5 comparable videos",
                (run_directory / "performance-report.md").read_text(encoding="utf-8"),
            )

    def test_generic_and_project_installers_refuse_then_backup_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            generic_root = base / "generic-skills"
            installed = run_script(
                INSTALL,
                "--client",
                "generic",
                "--target",
                generic_root,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            destination = generic_root / "analyze-creator-content"
            self.assertTrue((destination / "SKILL.md").is_file())

            refused = run_script(
                INSTALL,
                "--client",
                "generic",
                "--target",
                generic_root,
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("Refusing to overwrite", refused.stderr)

            marker = destination / "local-marker.txt"
            marker.write_text("previous install", encoding="utf-8")
            replaced = run_script(
                INSTALL,
                "--client",
                "generic",
                "--target",
                generic_root,
                "--replace",
            )
            self.assertEqual(replaced.returncode, 0, replaced.stderr)
            backups = list(generic_root.glob("analyze-creator-content.backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / "local-marker.txt").read_text(), "previous install")
            self.assertFalse((destination / "local-marker.txt").exists())

            project = base / "project"
            project.mkdir()
            for client, hidden in (("codex", ".agents"), ("claude", ".claude")):
                result = run_script(
                    INSTALL,
                    "--client",
                    client,
                    "--scope",
                    "project",
                    "--project",
                    project,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(
                    (project / hidden / "skills" / "analyze-creator-content" / "SKILL.md").is_file()
                )

    def test_user_install_paths_are_client_specific(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            env = os.environ.copy()
            env["HOME"] = temporary
            env["USERPROFILE"] = temporary
            for client, hidden in (("codex", ".agents"), ("claude", ".claude")):
                result = run_script(INSTALL, "--client", client, env=env)
                self.assertEqual(result.returncode, 0, result.stderr)
                expected = Path(temporary) / hidden / "skills" / "analyze-creator-content"
                self.assertTrue((expected / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()

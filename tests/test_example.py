from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "synthetic-social-lab"
BUILD = ROOT / "skills" / "analyze-creator-content" / "scripts" / "build_creator_library.py"


class SyntheticExampleTests(unittest.TestCase):
    def test_example_rebuilds_with_patterns_breakout_and_honest_gap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run_directory = Path(temporary) / "synthetic-social-lab"
            run_directory.mkdir()
            for filename in ("run.json", "source-inventory.jsonl", "content-library.jsonl"):
                shutil.copy2(EXAMPLE / filename, run_directory / filename)

            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            built = subprocess.run(
                [
                    sys.executable,
                    str(BUILD),
                    "--directory",
                    str(run_directory),
                    "--allow-incomplete",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                env=environment,
            )
            self.assertEqual(built.returncode, 0, built.stderr)

            summary = json.loads((run_directory / "library-summary.json").read_text())
            self.assertTrue(summary["inventory_complete"])
            self.assertTrue(summary["record_coverage_complete"])
            self.assertFalse(summary["source_access_complete"])
            self.assertFalse(summary["overall_coverage_complete"])
            self.assertEqual(summary["inventory_count"], 6)
            self.assertEqual(summary["relevant_count"], 5)
            self.assertEqual(summary["content_pillars"]["conversation skills"], 2)
            self.assertEqual(len(summary["reused_script_patterns"]), 2)

            performance = summary["performance"]
            self.assertEqual(performance["median_visible_count"], 1200)
            self.assertEqual(performance["creator_relative_breakout_count"], 1)
            self.assertEqual(
                performance["creator_relative_breakouts"][0]["source_id"], "v05"
            )
            self.assertEqual(
                performance["creator_relative_breakouts"][0]["multiple_of_median"], 5.0
            )

            coverage = (run_directory / "coverage-report.md").read_text()
            self.assertIn("Source access complete: no", coverage)
            self.assertIn("Overall coverage complete: no", coverage)
            self.assertIn("- v06", coverage)

            for filename in (
                "content-library.csv",
                "library-summary.json",
                "pattern-playbook.md",
                "performance-report.md",
                "coverage-report.md",
            ):
                self.assertEqual(
                    (run_directory / filename).read_text(encoding="utf-8"),
                    (EXAMPLE / filename).read_text(encoding="utf-8"),
                    f"Regenerate the committed synthetic output: {filename}",
                )


if __name__ == "__main__":
    unittest.main()

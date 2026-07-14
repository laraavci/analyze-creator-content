from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = ROOT / "skills" / "analyze-creator-content" / "scripts"
INIT = SKILL_SCRIPTS / "init_creator_library.py"
FINALIZE = SKILL_SCRIPTS / "finalize_inventory.py"
BUILD = SKILL_SCRIPTS / "build_creator_library.py"


def run_script(script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(script), *(str(value) for value in arguments)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=environment,
    )


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def inventory_row(
    source_id: str,
    *,
    creator: str = "demo-creator",
    platform: str = "example",
    status: str = "accessible",
    source_url: str | None = None,
) -> dict[str, object]:
    return {
        "source_id": source_id,
        "source_url": source_url or f"https://example.test/posts/{source_id}",
        "platform": platform,
        "creator": creator,
        "media_type": "video",
        "published_at": "2026-01-10",
        "status": status,
        "discovery_basis": "test manifest",
    }


def library_row(
    source_id: str,
    *,
    creator: str = "demo-creator",
    platform: str = "example",
    source_url: str | None = None,
    relevant: object = True,
    pattern: str = "Pain -> reframe -> steps -> CTA",
) -> dict[str, object]:
    row: dict[str, object] = {
        "source_id": source_id,
        "source_url": source_url or f"https://example.test/posts/{source_id}",
        "platform": platform,
        "creator": creator,
        "media_type": "video",
        "published_at": "2026-01-10",
        "review_basis": ["synthetic transcript", "synthetic frames"],
        "is_relevant": relevant,
        "confidence": "high",
        "topic": "making invitations specific",
        "content_pillar": "social skills",
        "content_type": "how-to or listicle",
        "format": "talking head",
        "hook_text": "Paraphrase: vague plans rarely become real plans.",
        "hook_excerpt": "",
        "hook_type": "pain recognition",
        "structure_beats": ["hook", "reframe", "steps", "CTA"],
        "cta": "save",
        "reusable_script_pattern": pattern,
        "research_claims": [],
        "exclusion_reason": "",
    }
    if relevant is False:
        row["confidence"] = "low"
        row["review_basis"] = ["access metadata only"]
        row["exclusion_reason"] = "Source was inaccessible."
        for field in ("topic", "content_type", "format", "hook_type", "structure_beats"):
            row.pop(field, None)
    return row


class CreatorLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

    def initialize(
        self,
        *,
        creator: str = "demo-creator",
        scope_kind: str = "full-profile",
    ) -> Path:
        directory = self.base / "run"
        completed = run_script(
            INIT,
            "--creator",
            creator,
            "--platform",
            "example",
            "--profile-url",
            "https://example.test/demo",
            "--scope-kind",
            scope_kind,
            "--scope",
            "all synthetic videos",
            "--output",
            directory,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return directory

    def finalize(
        self,
        directory: Path,
        expected: int,
        *,
        basis: str = "platform-enumerated-to-end",
        gaps: int = 0,
        status: str = "complete",
        extra: tuple[object, ...] = (),
    ) -> subprocess.CompletedProcess[str]:
        return run_script(
            FINALIZE,
            "--directory",
            directory,
            "--status",
            status,
            "--basis",
            basis,
            "--expected-items",
            expected,
            "--unresolved-gap-count",
            gaps,
            "--method",
            "synthetic fixture",
            *extra,
        )

    def test_init_refuses_nonempty_directory(self) -> None:
        directory = self.initialize()
        second = run_script(
            INIT,
            "--creator",
            "demo-creator",
            "--platform",
            "example",
            "--scope-kind",
            "full-profile",
            "--output",
            directory,
        )
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("Refusing to initialize non-empty directory", second.stderr)

    def test_complete_run_builds_source_linked_patterns(self) -> None:
        directory = self.initialize()
        inventory = [inventory_row("one"), inventory_row("two")]
        library = [library_row("one"), library_row("two")]
        write_jsonl(directory / "source-inventory.jsonl", inventory)
        write_jsonl(directory / "content-library.jsonl", library)
        finalized = self.finalize(directory, 2)
        self.assertEqual(finalized.returncode, 0, finalized.stderr)

        built = run_script(BUILD, "--directory", directory)
        self.assertEqual(built.returncode, 0, built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        self.assertTrue(summary["inventory_complete"])
        self.assertTrue(summary["record_coverage_complete"])
        self.assertTrue(summary["source_access_complete"])
        self.assertTrue(summary["overall_coverage_complete"])
        self.assertEqual(
            summary["reused_script_patterns"],
            {"Pain -> reframe -> steps -> CTA": 2},
        )
        playbook = (directory / "pattern-playbook.md").read_text()
        self.assertIn("Frequency: 2", playbook)
        self.assertIn("https://example.test/posts/one", playbook)
        performance_report = (directory / "performance-report.md").read_text()
        self.assertIn("No timestamped visible views or plays", performance_report)

    def test_placeholder_values_are_not_promoted_as_reused_patterns(self) -> None:
        directory = self.initialize()
        patterns = {
            "unknown-a": "unknown",
            "unknown-b": " UNKNOWN ",
            "unrecorded-a": "not recorded",
            "unrecorded-b": "Not Recorded",
            "real-a": "Question -> example -> invitation",
            "real-b": "Question -> example -> invitation",
        }
        write_jsonl(
            directory / "source-inventory.jsonl",
            [inventory_row(source_id) for source_id in patterns],
        )
        write_jsonl(
            directory / "content-library.jsonl",
            [
                library_row(source_id, pattern=pattern)
                for source_id, pattern in patterns.items()
            ],
        )
        self.assertEqual(self.finalize(directory, len(patterns)).returncode, 0)

        built = run_script(BUILD, "--directory", directory)
        self.assertEqual(built.returncode, 0, built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        self.assertEqual(
            summary["reused_script_patterns"],
            {"Question -> example -> invitation": 2},
        )
        playbook = (directory / "pattern-playbook.md").read_text()
        self.assertNotIn("### unknown", playbook.casefold())
        self.assertNotIn("### not recorded", playbook.casefold())
        self.assertIn("### Question -&gt; example -&gt; invitation", playbook)

    def test_summary_and_playbook_aggregate_topics_and_theme_metadata(self) -> None:
        directory = self.initialize()
        source_ids = ("one", "two", "three", "excluded")
        inventory = [inventory_row(source_id) for source_id in source_ids]
        library = []
        for source_id in source_ids[:3]:
            row = library_row(source_id)
            row.update(
                {
                    "content_pillar": "social skills",
                    "series_name": "Small Social Shifts",
                }
            )
            library.append(row)
        library[0].update(
            {
                "topic": "friendship invitations",
                "proof_device": "personal experience",
                "audience_job": "turn an acquaintance into a friend",
            }
        )
        library[1].update(
            {
                "topic": "friendship invitations",
                "proof_device": "named research",
                "audience_job": "turn an acquaintance into a friend",
            }
        )
        library[2].update(
            {
                "topic": "handling awkward silences",
                "proof_device": "demonstration",
                "audience_job": "handle awkward silences",
            }
        )
        excluded = library_row("excluded", relevant=False)
        excluded.update(
            {
                "exclusion_reason": "Outside the requested relevance lens.",
                "topic": "should not count",
                "content_pillar": "should not count",
                "series_name": "Should Not Count",
                "proof_device": "should not count",
                "audience_job": "should not count",
            }
        )
        library.append(excluded)
        write_jsonl(directory / "source-inventory.jsonl", inventory)
        write_jsonl(directory / "content-library.jsonl", library)
        self.assertEqual(self.finalize(directory, 4).returncode, 0)

        built = run_script(BUILD, "--directory", directory)
        self.assertEqual(built.returncode, 0, built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        self.assertEqual(summary["content_pillars"], {"social skills": 3})
        self.assertEqual(
            summary["topics"],
            {"friendship invitations": 2, "handling awkward silences": 1},
        )
        self.assertEqual(summary["series_names"], {"Small Social Shifts": 3})
        self.assertEqual(
            summary["proof_devices"],
            {"demonstration": 1, "named research": 1, "personal experience": 1},
        )
        self.assertEqual(
            summary["audience_jobs"],
            {
                "turn an acquaintance into a friend": 2,
                "handle awkward silences": 1,
            },
        )
        playbook = (directory / "pattern-playbook.md").read_text()
        self.assertIn("## Topics", playbook)
        self.assertIn("| friendship invitations | 2 |", playbook)
        self.assertIn("## Series Names", playbook)
        self.assertIn("## Proof Devices", playbook)
        self.assertIn("## Audience Jobs", playbook)

    def test_performance_report_surfaces_creator_relative_breakout(self) -> None:
        directory = self.initialize()
        counts = {
            "breakout": 1000,
            "base-a": 100,
            "base-b": 100,
            "base-c": 100,
            "base-d": 100,
            "base-e": 100,
        }
        inventory = [inventory_row(source_id) for source_id in counts]
        library = []
        for source_id, count in counts.items():
            row = library_row(source_id)
            row["visible_metrics"] = {
                "views": count,
                "likes": count // 10,
                "checked_at": "2026-07-14T12:00:00+00:00",
            }
            library.append(row)
        write_jsonl(directory / "source-inventory.jsonl", inventory)
        write_jsonl(directory / "content-library.jsonl", library)
        self.assertEqual(self.finalize(directory, 6).returncode, 0)

        built = run_script(BUILD, "--directory", directory)
        self.assertEqual(built.returncode, 0, built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        performance = summary["performance"]
        self.assertEqual(performance["comparison_metric"], "views")
        self.assertEqual(performance["comparable_video_count"], 6)
        self.assertEqual(performance["median_visible_count"], 100.0)
        self.assertTrue(performance["breakout_baseline_eligible"])
        self.assertEqual(performance["creator_relative_breakout_count"], 1)
        self.assertEqual(
            performance["creator_relative_breakouts"][0]["source_id"],
            "breakout",
        )
        self.assertEqual(
            performance["creator_relative_breakouts"][0]["multiple_of_median"],
            10.0,
        )
        report = (directory / "performance-report.md").read_text()
        self.assertIn("Creator-relative breakout candidates: 1", report)
        self.assertIn("<https://example.test/posts/breakout>", report)
        self.assertIn("2026-07-14T12:00:00+00:00", report)
        self.assertIn("10.00x", report)

    def test_small_metric_sample_ranks_without_breakout_label(self) -> None:
        directory = self.initialize()
        counts = {"top": 1000, "base-a": 100, "base-b": 100}
        inventory = [inventory_row(source_id) for source_id in counts]
        library = []
        for source_id, count in counts.items():
            row = library_row(source_id)
            row["visible_metrics"] = {
                "views": count,
                "checked_at": "2026-07-14T12:00:00Z",
            }
            library.append(row)
        write_jsonl(directory / "source-inventory.jsonl", inventory)
        write_jsonl(directory / "content-library.jsonl", library)
        self.assertEqual(self.finalize(directory, 3).returncode, 0)

        built = run_script(BUILD, "--directory", directory)
        self.assertEqual(built.returncode, 0, built.stderr)
        performance = json.loads(
            (directory / "library-summary.json").read_text()
        )["performance"]
        self.assertFalse(performance["breakout_baseline_eligible"])
        self.assertEqual(performance["creator_relative_breakout_count"], 0)
        self.assertEqual(performance["top_videos"][0]["source_id"], "top")
        report = (directory / "performance-report.md").read_text()
        self.assertIn("fewer than 5 comparable videos", report)

    def test_mixed_view_and_play_metrics_are_not_combined(self) -> None:
        directory = self.initialize()
        metric_rows = (
            ("view-a", "views", 1000),
            ("view-b", "views", 100),
            ("view-c", "views", 100),
            ("play-a", "plays", 50),
            ("play-b", "plays", 50),
            ("play-c", "plays", 50),
        )
        inventory = [inventory_row(source_id) for source_id, _, _ in metric_rows]
        library = []
        for source_id, metric_name, count in metric_rows:
            row = library_row(source_id)
            row["visible_metrics"] = {
                metric_name: count,
                "checked_at": "2026-07-14T12:00:00Z",
            }
            library.append(row)
        write_jsonl(directory / "source-inventory.jsonl", inventory)
        write_jsonl(directory / "content-library.jsonl", library)
        self.assertEqual(self.finalize(directory, 6).returncode, 0)

        built = run_script(BUILD, "--directory", directory)
        self.assertEqual(built.returncode, 0, built.stderr)
        performance = json.loads(
            (directory / "library-summary.json").read_text()
        )["performance"]
        self.assertEqual(performance["comparison_metric"], "views")
        self.assertEqual(performance["comparable_video_count"], 3)
        self.assertEqual(performance["alternate_metric_video_count"], 3)
        self.assertEqual(performance["creator_relative_breakout_count"], 0)

    def test_visible_metrics_require_valid_counts_and_timestamp(self) -> None:
        cases = (
            ("not an object", [], "visible_metrics must be a JSON object"),
            (
                "string count",
                {"views": "100", "checked_at": "2026-07-14T12:00:00Z"},
                "visible_metrics.views must be a non-negative integer",
            ),
            (
                "missing timestamp",
                {"views": 100},
                "visible_metrics.checked_at must be an ISO 8601 timestamp with timezone",
            ),
        )
        for label, metrics, expected in cases:
            with self.subTest(label=label):
                directory = self.base / ("metrics-" + label.replace(" ", "-"))
                initialized = run_script(
                    INIT,
                    "--creator",
                    "demo-creator",
                    "--platform",
                    "example",
                    "--scope-kind",
                    "supplied-links",
                    "--output",
                    directory,
                )
                self.assertEqual(initialized.returncode, 0, initialized.stderr)
                write_jsonl(
                    directory / "source-inventory.jsonl", [inventory_row("one")]
                )
                row = library_row("one")
                row["visible_metrics"] = metrics
                write_jsonl(directory / "content-library.jsonl", [row])
                built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
                self.assertNotEqual(built.returncode, 0)
                self.assertIn(expected, built.stderr)

    def test_full_profile_rejects_supplied_set_completion(self) -> None:
        directory = self.initialize()
        write_jsonl(directory / "source-inventory.jsonl", [inventory_row("one")])
        completed = self.finalize(directory, 1, basis="user-supplied-set")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("cannot complete scope 'full-profile'", completed.stderr)

    def test_known_count_gap_cannot_be_marked_complete(self) -> None:
        directory = self.initialize()
        write_jsonl(
            directory / "source-inventory.jsonl",
            [inventory_row("one"), inventory_row("two")],
        )
        completed = self.finalize(
            directory,
            2,
            basis="known-count-reconciled",
            extra=("--profile-stated-count", 3),
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("must equal --expected-items", completed.stderr)

    def test_invalid_inventory_timestamp_is_rejected(self) -> None:
        directory = self.initialize()
        write_jsonl(directory / "source-inventory.jsonl", [inventory_row("one")])
        completed = self.finalize(
            directory,
            1,
            extra=("--checked-at", "not-a-timestamp"),
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("ISO 8601 timestamp with timezone", completed.stderr)

    def test_unknown_denominator_never_reports_complete(self) -> None:
        directory = self.initialize()
        write_jsonl(directory / "source-inventory.jsonl", [inventory_row("one")])
        write_jsonl(directory / "content-library.jsonl", [library_row("one")])
        built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
        self.assertEqual(built.returncode, 0, built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        self.assertFalse(summary["inventory_complete"])
        self.assertFalse(summary["overall_coverage_complete"])
        self.assertIn("inventory_status is not complete", summary["inventory_completion_reasons"])

    def test_profile_count_700_with_three_rows_cannot_auto_complete(self) -> None:
        directory = self.initialize()
        run = json.loads((directory / "run.json").read_text(encoding="utf-8"))
        run["profile_stated_count"] = 700
        (directory / "run.json").write_text(
            json.dumps(run, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_jsonl(
            directory / "source-inventory.jsonl",
            [inventory_row("one"), inventory_row("two"), inventory_row("three")],
        )
        write_jsonl(
            directory / "content-library.jsonl",
            [library_row("one"), library_row("two"), library_row("three")],
        )
        built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
        self.assertEqual(built.returncode, 0, built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        self.assertFalse(summary["inventory_complete"])
        self.assertFalse(summary["overall_coverage_complete"])

    def test_inaccessible_source_keeps_overall_coverage_incomplete(self) -> None:
        directory = self.initialize()
        write_jsonl(
            directory / "source-inventory.jsonl",
            [inventory_row("one", status="inaccessible")],
        )
        write_jsonl(
            directory / "content-library.jsonl",
            [library_row("one", relevant=False)],
        )
        finalized = self.finalize(directory, 1)
        self.assertEqual(finalized.returncode, 0, finalized.stderr)
        built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
        self.assertEqual(built.returncode, 0, built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        self.assertTrue(summary["inventory_complete"])
        self.assertTrue(summary["record_coverage_complete"])
        self.assertFalse(summary["source_access_complete"])
        self.assertFalse(summary["overall_coverage_complete"])
        self.assertEqual(summary["unavailable_source_ids"], ["one"])

    def test_missing_library_record_builds_only_as_explicit_partial(self) -> None:
        directory = self.initialize()
        write_jsonl(
            directory / "source-inventory.jsonl",
            [inventory_row("one"), inventory_row("two")],
        )
        write_jsonl(directory / "content-library.jsonl", [library_row("one")])
        self.assertEqual(self.finalize(directory, 2).returncode, 0)
        built = run_script(BUILD, "--directory", directory)
        self.assertNotEqual(built.returncode, 0)
        self.assertIn("overall coverage is incomplete", built.stderr)
        summary = json.loads((directory / "library-summary.json").read_text())
        self.assertFalse(summary["record_coverage_complete"])
        self.assertEqual(summary["missing_source_ids"], ["two"])

    def test_mismatched_source_metadata_is_rejected(self) -> None:
        directory = self.initialize()
        write_jsonl(directory / "source-inventory.jsonl", [inventory_row("one")])
        write_jsonl(
            directory / "content-library.jsonl",
            [library_row("one", source_url="https://example.test/posts/wrong")],
        )
        built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
        self.assertNotEqual(built.returncode, 0)
        self.assertIn("source_url does not match inventory", built.stderr)

    def test_empty_url_string_boolean_and_long_excerpt_are_rejected(self) -> None:
        cases = (
            ("empty source URL", {"source_url": ""}, "source_url must be a non-empty string"),
            (
                "empty content pillar",
                {"content_pillar": ""},
                "content_pillar must be non-empty when relevant",
            ),
            ("string Boolean", {"is_relevant": "true"}, "is_relevant must be true or false"),
            (
                "long excerpt",
                {"hook_excerpt": "one two three four five six seven eight nine ten eleven twelve thirteen"},
                "exceeds the 12-word limit",
            ),
        )
        for label, mutation, expected in cases:
            with self.subTest(label=label):
                directory = self.base / label.replace(" ", "-")
                initialized = run_script(
                    INIT,
                    "--creator",
                    "demo-creator",
                    "--platform",
                    "example",
                    "--scope-kind",
                    "supplied-links",
                    "--output",
                    directory,
                )
                self.assertEqual(initialized.returncode, 0, initialized.stderr)
                write_jsonl(directory / "source-inventory.jsonl", [inventory_row("one")])
                row = library_row("one")
                row.update(mutation)
                write_jsonl(directory / "content-library.jsonl", [row])
                built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
                self.assertNotEqual(built.returncode, 0)
                self.assertIn(expected, built.stderr)

    def test_malformed_run_json_has_friendly_error_without_traceback(self) -> None:
        directory = self.initialize()
        (directory / "run.json").write_text("{not json", encoding="utf-8")
        built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
        self.assertNotEqual(built.returncode, 0)
        self.assertIn("invalid JSON", built.stderr)
        self.assertNotIn("Traceback", built.stderr)

    def test_full_transcript_is_rejected_from_durable_library(self) -> None:
        directory = self.initialize(scope_kind="supplied-links")
        write_jsonl(directory / "source-inventory.jsonl", [inventory_row("one")])
        row = library_row("one")
        row["full_transcript"] = "Synthetic long-form source text."
        write_jsonl(directory / "content-library.jsonl", [row])
        built = run_script(BUILD, "--directory", directory, "--allow-incomplete")
        self.assertNotEqual(built.returncode, 0)
        self.assertIn("forbidden durable fields: full_transcript", built.stderr)

    def test_generated_csv_and_markdown_neutralize_untrusted_labels(self) -> None:
        directory = self.initialize(creator="formula-demo", scope_kind="supplied-links")
        inventory = [inventory_row("one", creator="formula-demo")]
        row = library_row("one", creator="formula-demo")
        row["topic"] = "=2+2"
        row["content_pillar"] = "bad|pillar\n# injected heading"
        row["hook_text"] = "[click here](https://malicious.example)"
        row["visible_metrics"] = {
            "views": 100,
            "checked_at": "2026-07-14T12:00:00Z",
        }
        write_jsonl(directory / "source-inventory.jsonl", inventory)
        write_jsonl(directory / "content-library.jsonl", [row])
        finalized = self.finalize(directory, 1, basis="user-supplied-set")
        self.assertEqual(finalized.returncode, 0, finalized.stderr)
        built = run_script(BUILD, "--directory", directory)
        self.assertEqual(built.returncode, 0, built.stderr)
        with (directory / "content-library.csv").open(newline="", encoding="utf-8") as handle:
            csv_row = next(csv.DictReader(handle))
        self.assertEqual(csv_row["topic"], "'=2+2")
        playbook = (directory / "pattern-playbook.md").read_text(encoding="utf-8")
        self.assertIn("bad\\|pillar # injected heading", playbook)
        self.assertNotIn("\n# injected heading", playbook)
        performance = (directory / "performance-report.md").read_text(encoding="utf-8")
        self.assertIn("\\[click here\\](https://malicious.example)", performance)
        self.assertNotIn("[click here](https://malicious.example)", performance)


if __name__ == "__main__":
    unittest.main()

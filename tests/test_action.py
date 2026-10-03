import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from action import Check, evaluate_repository, main, render_summary


class EvaluateRepositoryTests(unittest.TestCase):
    def test_complete_repository_reports_present_signals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (
                "README.md",
                "LICENSE",
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                ".github/workflows/ci.yml",
                ".github/ISSUE_TEMPLATE/bug.md",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("example", encoding="utf-8")

            checks = evaluate_repository(root, release_tags=["v1.0.0"])

        self.assertEqual(len(checks), 7)
        self.assertTrue(all(check.found is True for check in checks))

    def test_empty_repository_returns_advisory_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            checks = evaluate_repository(Path(directory), release_tags=[])

        self.assertEqual(len(checks), 7)
        self.assertTrue(all(check.found is False for check in checks))
        self.assertTrue(all(check.recommendation for check in checks))

    def test_summary_is_informative_and_escapes_table_delimiters(self):
        summary = render_summary(
            [
                Check(
                    name="Check | one",
                    found=False,
                    evidence="Missing | file",
                    recommendation="Add it",
                )
            ]
        )

        self.assertIn("0 of 1 checks found a readiness signal", summary)
        self.assertIn("Check \\| one", summary)
        self.assertIn("Missing \\| file Add it", summary)
        self.assertIn("does not fail the workflow", summary)

    def test_main_appends_report_to_github_step_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary_path = root / "step-summary.md"
            summary_path.write_text("Earlier step\n", encoding="utf-8")
            with patch.dict(
                os.environ,
                {
                    "GITHUB_WORKSPACE": str(root),
                    "GITHUB_STEP_SUMMARY": str(summary_path),
                },
            ):
                result = main()

            output = summary_path.read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertTrue(output.startswith("Earlier step\n# Repository readiness report"))
        self.assertIn("| Release history |", output)


if __name__ == "__main__":
    unittest.main()

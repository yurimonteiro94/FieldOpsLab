from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_SCRIPTS_DIR = PROJECT_ROOT / "analysis" / "scripts"


AUXILIARY_SCRIPT_FILENAMES = [
    "audit_batch_recommendations.py",
    "generate_batch_markdown_report.py",
    "generate_campaign_index.py",
    "generate_fuzzy_decision_report.py",
    "generate_scenario_descriptors.py",
    "inspect_batch_config_schema.py",
    "run_batch_analysis_pipeline.py",
    "run_ranking_sensitivity.py",
    "summarize_batch_result.py",
    "verify_analysis_outputs.py",
    "verify_campaign_index.py",
    "verify_executed_campaign_batch_result_paths.py",
]


class AuxiliaryAnalysisScriptContractTests(unittest.TestCase):
    def script_path(self, filename: str) -> Path:
        return ANALYSIS_SCRIPTS_DIR / filename

    def script_source(self, filename: str) -> str:
        return self.script_path(filename).read_text(encoding="utf-8")

    def test_auxiliary_analysis_scripts_exist(self) -> None:
        missing = [
            filename
            for filename in AUXILIARY_SCRIPT_FILENAMES
            if not self.script_path(filename).is_file()
        ]

        self.assertFalse(
            missing,
            f"Missing expected auxiliary analysis script(s): {missing}",
        )

    def test_auxiliary_analysis_scripts_compile(self) -> None:
        for filename in AUXILIARY_SCRIPT_FILENAMES:
            with self.subTest(script=filename):
                completed = subprocess.run(
                    [
                        "py",
                        "-3",
                        "-m",
                        "py_compile",
                        str(self.script_path(filename)),
                    ],
                    cwd=PROJECT_ROOT,
                    text=True,
                    capture_output=True,
                )

                self.assertEqual(
                    completed.returncode,
                    0,
                    completed.stdout + completed.stderr,
                )

    def test_auxiliary_analysis_scripts_have_main_guard(self) -> None:
        main_guard_pattern = re.compile(
            r"if\s+__name__\s*==\s*['\"]__main__['\"]\s*:"
        )

        for filename in AUXILIARY_SCRIPT_FILENAMES:
            with self.subTest(script=filename):
                source = self.script_source(filename)

                self.assertRegex(
                    source,
                    main_guard_pattern,
                    f"{filename} must have an explicit __main__ guard.",
                )

    def test_auxiliary_analysis_scripts_call_main_from_main_guard(self) -> None:
        for filename in AUXILIARY_SCRIPT_FILENAMES:
            with self.subTest(script=filename):
                source = self.script_source(filename)

                self.assertIn(
                    "main(",
                    source,
                    f"{filename} should expose a main() entry point.",
                )

                self.assertTrue(
                    "raise SystemExit(main())" in source
                    or "sys.exit(main())" in source
                    or "main()" in source,
                    f"{filename} should call main() from its CLI entry point.",
                )

    def test_auxiliary_cli_scripts_expose_argument_or_usage_contract(self) -> None:
        allowed_simple_inspection_scripts = {
            "inspect_batch_config_schema.py",
        }

        for filename in AUXILIARY_SCRIPT_FILENAMES:
            with self.subTest(script=filename):
                source = self.script_source(filename)

                if filename in allowed_simple_inspection_scripts:
                    continue

                has_argument_contract = (
                    "sys.argv" in source
                    or "argparse" in source
                    or "Usage:" in source
                    or "usage:" in source
                )

                self.assertTrue(
                    has_argument_contract,
                    f"{filename} should expose an argument/usage contract.",
                )

    def test_auxiliary_analysis_scripts_are_not_temporary_patch_scripts(self) -> None:
        for filename in AUXILIARY_SCRIPT_FILENAMES:
            with self.subTest(script=filename):
                self.assertFalse(
                    filename.startswith("patch_"),
                    f"{filename} must not be a temporary patch script.",
                )


if __name__ == "__main__":
    unittest.main()
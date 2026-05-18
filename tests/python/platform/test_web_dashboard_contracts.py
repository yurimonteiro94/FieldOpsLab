## 21. `tests\python\platform\test_web_dashboard_contracts.py`

from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WEB_ROOT = PROJECT_ROOT / "apps" / "web"


class WebDashboardContractTests(unittest.TestCase):
    def test_required_web_files_exist(self) -> None:
        required_files = [
            WEB_ROOT / "package.json",
            WEB_ROOT / "index.html",
            WEB_ROOT / "tsconfig.json",
            WEB_ROOT / "vite.config.ts",
            WEB_ROOT / "README.md",
            WEB_ROOT / "src" / "main.tsx",
            WEB_ROOT / "src" / "App.tsx",
            WEB_ROOT / "src" / "styles.css",
            WEB_ROOT / "src" / "domain" / "platform.ts",
            WEB_ROOT / "src" / "services" / "readOnlyPlatformApi.ts",
            WEB_ROOT / "src" / "viewModels" / "useDashboardViewModel.ts",
            WEB_ROOT / "src" / "components" / "Layout.tsx",
            WEB_ROOT / "src" / "components" / "StatusCard.tsx",
            WEB_ROOT / "src" / "components" / "ReportCard.tsx",
            WEB_ROOT / "src" / "pages" / "DashboardPage.tsx",
            WEB_ROOT / "src" / "__tests__" / "readOnlyPlatformApi.test.ts",
            WEB_ROOT / "src" / "__tests__" / "DashboardPage.test.tsx",
        ]

        for path in required_files:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"Missing required web file: {path}")
                self.assertGreater(
                    path.stat().st_size,
                    0,
                    f"Required web file is empty: {path}",
                )

    def test_package_json_exposes_required_scripts(self) -> None:
        package_json = json.loads((WEB_ROOT / "package.json").read_text(encoding="utf-8"))

        scripts = package_json["scripts"]

        self.assertIn("dev", scripts)
        self.assertIn("build", scripts)
        self.assertIn("test", scripts)
        self.assertIn("test:run", scripts)
        self.assertIn("typecheck", scripts)

    def test_web_architecture_uses_expected_layers(self) -> None:
        expected_directories = [
            WEB_ROOT / "src" / "domain",
            WEB_ROOT / "src" / "services",
            WEB_ROOT / "src" / "viewModels",
            WEB_ROOT / "src" / "components",
            WEB_ROOT / "src" / "pages",
            WEB_ROOT / "src" / "__tests__",
        ]

        for path in expected_directories:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"Missing web architecture folder: {path}")
                self.assertTrue(path.is_dir(), f"Expected folder is not a directory: {path}")

    def test_web_dashboard_is_read_only_and_does_not_expose_execution(self) -> None:
        combined_source = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (WEB_ROOT / "src").rglob("*")
            if path.is_file() and path.suffix in {".ts", ".tsx"}
        )

        forbidden_fragments = [
            "/api/v1/execute",
            "/api/v1/run-command",
            "arbitrary command execution is allowed",
            "scientific validity proven",
        ]

        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, combined_source)

        self.assertIn("read-only", combined_source)
        self.assertIn("does not prove scientific validity", combined_source)

    def test_web_readme_does_not_overstate_maturity(self) -> None:
        readme_text = (WEB_ROOT / "README.md").read_text(encoding="utf-8").lower()

        self.assertIn("current product completeness estimate: 39%", readme_text)
        self.assertIn("does not prove scientific validity", readme_text)
        self.assertIn("does not execute backend commands", readme_text)


if __name__ == "__main__":
    unittest.main()
from __future__ import annotations

import ast
import importlib.util
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPOSITORY_ROOT / "deploy" / "cloud-run" / "smoke_test_read_only_api_container.py"
README_PATH = REPOSITORY_ROOT / "deploy" / "cloud-run" / "README.md"


def load_smoke_script_module():
    spec = importlib.util.spec_from_file_location(
        "smoke_test_read_only_api_container",
        SCRIPT_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReadOnlyApiContainerSmokeScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.script = SCRIPT_PATH.read_text(encoding="utf-8")
        self.readme = README_PATH.read_text(encoding="utf-8")

    def test_script_exists_and_compiles(self) -> None:
        self.assertTrue(SCRIPT_PATH.exists())
        ast.parse(self.script)

    def test_script_has_main_guard(self) -> None:
        self.assertIn('if __name__ == "__main__":', self.script)
        self.assertIn("raise SystemExit(main(sys.argv[1:]))", self.script)

    def test_script_streams_docker_build_output(self) -> None:
        self.assertIn("def run_streamed_command", self.script)
        self.assertIn("subprocess.Popen", self.script)
        self.assertIn("for line in process.stdout", self.script)
        self.assertIn("print(line, end=\"\", flush=True)", self.script)
        self.assertIn("build_image", self.script)
        self.assertIn("run_streamed_command", self.script)

    def test_script_uses_utf8_with_replacement_for_subprocess_output(self) -> None:
        self.assertIn('encoding="utf-8"', self.script)
        self.assertIn('errors="replace"', self.script)

    def test_script_stops_container_in_finally_block(self) -> None:
        self.assertIn("finally:", self.script)
        self.assertIn("stop_container(container_id)", self.script)
        self.assertIn("remove_named_container(args.container_name)", self.script)
        self.assertIn("stop_containers_publishing_port(args.port)", self.script)

    def test_script_validates_read_only_safety_flags(self) -> None:
        module = load_smoke_script_module()

        valid_payload = {
            "status": "ok",
            "read_only": True,
            "execution_enabled": False,
            "browser_triggered_execution_enabled": False,
            "write_operations_supported": False,
            "endpoints": module.REQUIRED_ENDPOINTS,
        }

        module.validate_health_payload(valid_payload)

        invalid_payload = dict(valid_payload)
        invalid_payload["execution_enabled"] = True

        with self.assertRaises(module.SmokeTestError):
            module.validate_health_payload(invalid_payload)

    def test_script_rejects_duplicate_or_non_string_endpoints(self) -> None:
        module = load_smoke_script_module()

        duplicate_payload = {
            "status": "ok",
            "read_only": True,
            "execution_enabled": False,
            "browser_triggered_execution_enabled": False,
            "write_operations_supported": False,
            "endpoints": module.REQUIRED_ENDPOINTS + [module.REQUIRED_ENDPOINTS[0]],
        }

        with self.assertRaises(module.SmokeTestError):
            module.validate_health_payload(duplicate_payload)

        non_string_payload = {
            "status": "ok",
            "read_only": True,
            "execution_enabled": False,
            "browser_triggered_execution_enabled": False,
            "write_operations_supported": False,
            "endpoints": module.REQUIRED_ENDPOINTS + [["/api/v1/bad", 200]],
        }

        with self.assertRaises(module.SmokeTestError):
            module.validate_health_payload(non_string_payload)

    def test_script_declares_required_endpoint_catalog(self) -> None:
        module = load_smoke_script_module()

        self.assertIn("/api/v1/health", module.REQUIRED_ENDPOINTS)
        self.assertIn("/api/v1/solver-integration-contract", module.REQUIRED_ENDPOINTS)
        self.assertIn("/api/v1/comparative-analysis-sample", module.REQUIRED_ENDPOINTS)
        self.assertIn("/api/v1/deployment-readiness-contract", module.REQUIRED_ENDPOINTS)
        self.assertIn("/api/v1/simulation-playback-state-sample", module.REQUIRED_ENDPOINTS)

    def test_readme_documents_automated_smoke_test_helper(self) -> None:
        lowered = self.readme.lower()

        self.assertIn("automated local smoke test command", lowered)
        self.assertIn("py -3 deploy\\cloud-run\\smoke_test_read_only_api_container.py", self.readme)
        self.assertIn("stops existing containers publishing port 8080", lowered)
        self.assertIn("validates the unknown-report 404 behavior", lowered)
        self.assertIn("validates that post requests still return http 405", lowered)
        self.assertIn("stops the container at the end", lowered)

    def test_readme_documents_manual_port_release(self) -> None:
        lowered = self.readme.lower()

        self.assertIn("stop containers using port 8080", lowered)
        self.assertIn('docker ps --filter "publish=8080"', self.readme)
        self.assertIn("docker stop", self.readme)
        self.assertIn('netstat -ano | findstr ":8080"', self.readme)
        self.assertIn("time_wait", lowered)


if __name__ == "__main__":
    unittest.main()
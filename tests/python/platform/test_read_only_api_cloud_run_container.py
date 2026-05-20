## 4. Arquivo `tests\python\platform\test_read_only_api_cloud_run_container.py`

import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DOCKERFILE_PATH = REPOSITORY_ROOT / "deploy" / "cloud-run" / "read_only_api.Dockerfile"
README_PATH = REPOSITORY_ROOT / "deploy" / "cloud-run" / "README.md"


class ReadOnlyApiCloudRunContainerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")
        self.readme = README_PATH.read_text(encoding="utf-8")

    def test_dockerfile_exists_and_uses_python_runtime(self) -> None:
        self.assertTrue(DOCKERFILE_PATH.exists())
        lowered = self.dockerfile.lower()
        self.assertIn("from python:", lowered)
        self.assertIn("slim", lowered)

    def test_dockerfile_copies_required_read_only_artifacts(self) -> None:
        lowered = self.dockerfile.lower()
        self.assertIn("copy services", lowered)
        self.assertIn("copy analysis/reports", lowered)
        self.assertIn("copy platform/contracts", lowered)
        self.assertIn("fieldops_http_server.py", lowered)

    def test_dockerfile_serves_read_only_api_on_cloud_run_port(self) -> None:
        lowered = self.dockerfile.lower()
        self.assertIn("port", lowered)
        self.assertIn("0.0.0.0", lowered)
        self.assertIn("fieldops_http_server.py", lowered)
        self.assertIn("--host", lowered)
        self.assertIn("--port", lowered)

    def test_dockerfile_runs_as_non_root_user(self) -> None:
        lowered = self.dockerfile.lower()
        self.assertIn("useradd", lowered)
        self.assertIn("user fieldops", lowered)

    def test_container_scaffold_does_not_claim_solver_execution(self) -> None:
        lowered = self.readme.lower()
        self.assertIn("does not run solvers", lowered)
        self.assertIn("does not start experiments", lowered)
        self.assertIn("does not mutate schedules", lowered)
        self.assertIn("does not write files", lowered)
        self.assertIn("does not trigger backend jobs", lowered)

    def test_readme_documents_local_build_and_run(self) -> None:
        self.assertIn("docker build", self.readme)
        self.assertIn("docker run", self.readme)
        self.assertIn("fieldops-read-only-api", self.readme)
        self.assertIn("curl http://127.0.0.1:8080/api/v1/health", self.readme)

    def test_readme_documents_future_cloud_run_deploy_without_forcing_it(self) -> None:
        lowered = self.readme.lower()
        self.assertIn("gcloud run deploy", lowered)
        self.assertIn("future deployment command template", lowered)
        self.assertIn("do not run it until", lowered)
        self.assertIn("smoke-tested successfully", lowered)

    def test_readme_requires_post_deploy_smoke_tests(self) -> None:
        lowered = self.readme.lower()
        self.assertIn("required smoke tests after deploy", lowered)
        self.assertIn("/api/v1/health", lowered)
        self.assertIn("/api/v1/project-status", lowered)
        self.assertIn("/api/v1/deployment-readiness-contract", lowered)
        self.assertIn("post request", lowered)
        self.assertIn("http 405", lowered)

    def test_readme_exposes_current_read_only_endpoints(self) -> None:
        lowered = self.readme.lower()
        self.assertIn("/api/v1/solver-integration-contract", lowered)
        self.assertIn("/api/v1/comparative-analysis-contract", lowered)
        self.assertIn("/api/v1/comparative-analysis-sample", lowered)
        self.assertIn("/api/v1/deployment-readiness-contract", lowered)

    def test_readme_is_honest_about_remaining_production_work(self) -> None:
        lowered = self.readme.lower()
        self.assertIn("does not make the full fieldops lab system production-ready", lowered)
        self.assertIn("real execution layer", lowered)
        self.assertIn("remaining work includes", lowered)
        self.assertIn("or-tools-backed solver integration", lowered)
        self.assertIn("statistical analysis pipeline", lowered)


if __name__ == "__main__":
    unittest.main()
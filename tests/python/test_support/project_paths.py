from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    current = Path(__file__).resolve()

    for candidate in [current, *current.parents]:
        has_cmake = (candidate / "CMakeLists.txt").exists()
        has_analysis_scripts = (candidate / "analysis" / "scripts").exists()

        if has_cmake and has_analysis_scripts:
            return candidate

    raise RuntimeError("Could not locate FieldOpsLab project root.")


PROJECT_ROOT = project_root()
ANALYSIS_SCRIPTS_DIR = PROJECT_ROOT / "analysis" / "scripts"
ANALYSIS_REPORTS_DIR = PROJECT_ROOT / "analysis" / "reports"
DATA_RESULTS_DIR = PROJECT_ROOT / "data" / "results"
import json
from pathlib import Path
from typing import Dict


class PhaseReportVerifier:

    def __init__(self, base_directory="."):
        self.base_directory = Path(base_directory)

    def verify_report(
        self,
        phase_number: int,
        filename: str,
    ) -> Dict:

        path = (
            self.base_directory
            / "reports"
            / f"phase{phase_number}"
            / filename
        )

        if not path.exists():
            return {
                "phase": phase_number,
                "exists": False,
                "valid": False,
            }

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as handle:
                data = json.load(handle)

            return {
                "phase": phase_number,
                "exists": True,
                "valid": isinstance(data, dict),
                "path": str(path),
            }

        except Exception as exc:
            return {
                "phase": phase_number,
                "exists": True,
                "valid": False,
                "error": str(exc),
            }

    def verify_required_phases(self) -> Dict:

        reports = {
            23: "phase23_shadow_observation_report.json",
            24: "phase24_live_activation_readiness_report.json",
            25: "phase25_canary_operation_report.json",
            26: "phase26_canary_performance_report.json",
            27: "phase27_runtime_orchestration_report.json",
            28: "phase28_observability_report.json",
            29: "phase29_governance_readiness_report.json",
        }

        results = {}

        for phase, filename in reports.items():
            results[str(phase)] = self.verify_report(
                phase,
                filename,
            )

        passed = all(
            item["exists"] and item["valid"]
            for item in results.values()
        )

        return {
            "passed": passed,
            "reports": results,
        }

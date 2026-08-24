import json
from pathlib import Path
from typing import Dict

from workers.release_control.release_safety import (
    ReleaseSafetyController,
)
from workers.release_control.phase_report_verifier import (
    PhaseReportVerifier,
)
from workers.release_control.release_gate import (
    FinalReleaseGate,
)
from workers.release_control.release_readiness import (
    ReleaseReadiness,
)
from workers.release_control.release_audit_logger import (
    ReleaseAuditLogger,
)


class Phase30ReleaseWorker:

    def __init__(
        self,
        config,
        base_directory=".",
    ):

        self.config = config
        self.base_directory = Path(
            base_directory
        )

        self.report_directory = (
            self.base_directory
            / config.REPORT_DIRECTORY
        )

        self.report_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.audit = ReleaseAuditLogger(
            self.report_directory
            / config.AUDIT_FILENAME
        )

        self.safety = ReleaseSafetyController(
            config
        )

        self.verifier = PhaseReportVerifier(
            self.base_directory
        )

        self.gate = FinalReleaseGate(
            config,
            self.safety,
            self.verifier,
        )

        self.readiness = ReleaseReadiness()

    def run(self) -> Dict:

        self.audit.log(
            "PHASE30_START",
            {
                "live_trading_enabled":
                    self.config.LIVE_TRADING_ENABLED,
                "real_broker_enabled":
                    self.config.REAL_BROKER_ENABLED,
            },
        )

        gate = self.gate.evaluate()

        readiness = self.readiness.evaluate(
            gate
        )

        safety = self.safety.validate()

        report = {
            "phase": 30,
            "name": (
                "Production Session Control "
                "and Final Release Certification"
            ),
            "release_gate": gate,
            "readiness": readiness,
            "safety": safety,
            "real_orders_placed": 0,
            "live_trading_enabled": (
                self.config.LIVE_TRADING_ENABLED
            ),
            "real_broker_enabled": (
                self.config.REAL_BROKER_ENABLED
            ),
            "place_real_orders": (
                self.config.PLACE_REAL_ORDERS
            ),
        }

        report_path = (
            self.report_directory
            / self.config.REPORT_FILENAME
        )

        with report_path.open(
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                report,
                handle,
                indent=2,
            )

        self.audit.log(
            "PHASE30_COMPLETE",
            {
                "ready": readiness["ready"],
                "score": readiness["score"],
                "classification":
                    readiness["classification"],
            },
        )

        return report

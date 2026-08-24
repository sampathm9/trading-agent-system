import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

from workers.governance.audit_integrity import (
    AuditIntegrity,
)
from workers.governance.configuration_governance import (
    ConfigurationGovernance,
)
from workers.governance.deployment_verifier import (
    DeploymentVerifier,
)
from workers.governance.drift_detector import (
    DriftDetector,
)
from workers.governance.emergency_stop_verifier import (
    EmergencyStopVerifier,
)
from workers.governance.governance_readiness import (
    GovernanceReadiness,
)
from workers.governance.risk_policy_guard import (
    RiskPolicyGuard,
)
from workers.governance.session_authorizer import (
    SessionAuthorizer,
)


class Phase29GovernanceWorker:

    def __init__(self, config_module):

        self.config = config_module

        self.configuration = ConfigurationGovernance()

        self.deployment = DeploymentVerifier()

        self.session = SessionAuthorizer(
            config_module.ALLOWED_SESSIONS
        )

        self.risk = RiskPolicyGuard(
            max_order_quantity=(
                config_module.MAX_ORDER_QUANTITY
            ),
            max_daily_trades=(
                config_module.MAX_DAILY_TRADES
            ),
            max_daily_loss=(
                config_module.MAX_DAILY_LOSS
            ),
            max_consecutive_losses=(
                config_module.MAX_CONSECUTIVE_LOSSES
            ),
        )

        self.audit = AuditIntegrity()

        self.drift = DriftDetector()

        self.emergency = EmergencyStopVerifier()

        self.readiness = GovernanceReadiness()

    def run(self) -> Dict[str, Any]:

        config_result = self.configuration.validate(
            self.config
        )

        deployment_result = self.deployment.verify()

        session_result = self.session.authorize(
            session=self.config.DEFAULT_SESSION,
            live_trading_enabled=(
                self.config.LIVE_TRADING_ENABLED
            ),
        )

        risk_result = self.risk.validate(
            quantity=1,
            daily_trades=0,
            daily_loss=0.0,
            consecutive_losses=0,
        )

        baseline = {
            "live_trading_enabled": False,
            "real_broker_enabled": False,
            "place_real_orders": False,
            "paper_only": True,
        }

        current = {
            "live_trading_enabled": (
                self.config.LIVE_TRADING_ENABLED
            ),
            "real_broker_enabled": (
                self.config.REAL_BROKER_ENABLED
            ),
            "place_real_orders": (
                self.config.PLACE_REAL_ORDERS
            ),
            "paper_only": (
                self.config.PAPER_ONLY
            ),
        }

        drift_result = self.drift.compare(
            baseline,
            current,
        )

        emergency_result = (
            self.emergency.verify()
        )

        self.audit.record(
            "PHASE29_START",
            {
                "paper_only": True,
                "live_trading_enabled": False,
            },
        )

        self.audit.record(
            "CONFIGURATION_VALIDATED",
            {
                "passed": config_result["passed"],
            },
        )

        self.audit.record(
            "SESSION_AUTHORIZED",
            {
                "passed": session_result["authorized"],
            },
        )

        self.audit.record(
            "RISK_POLICY_VALIDATED",
            {
                "passed": risk_result["passed"],
            },
        )

        self.audit.record(
            "DRIFT_CHECKED",
            {
                "passed": drift_result["passed"],
            },
        )

        audit_result = self.audit.verify()

        checks = {
            "configuration_governance": (
                config_result["passed"]
            ),
            "deployment_verification": (
                deployment_result["passed"]
            ),
            "session_authorization": (
                session_result["authorized"]
            ),
            "risk_policy": (
                risk_result["passed"]
            ),
            "audit_integrity": (
                audit_result["passed"]
            ),
            "configuration_drift": (
                drift_result["passed"]
            ),
            "emergency_stop": (
                emergency_result["passed"]
            ),
            "live_trading_disabled": (
                self.config.LIVE_TRADING_ENABLED is False
            ),
            "real_broker_disabled": (
                self.config.REAL_BROKER_ENABLED is False
            ),
            "real_orders_disabled": (
                self.config.PLACE_REAL_ORDERS is False
            ),
            "paper_only": (
                self.config.PAPER_ONLY is True
            ),
        }

        readiness_result = self.readiness.evaluate(
            checks,
            minimum_score=(
                self.config.MIN_READINESS_SCORE
            ),
        )

        report = {
            "phase": 29,
            "title": (
                "Operational Governance and Compliance"
            ),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "configuration": config_result,
            "deployment": deployment_result,
            "session": session_result,
            "risk_policy": risk_result,
            "drift": drift_result,
            "emergency_stop": emergency_result,
            "audit_integrity": audit_result,
            "readiness": readiness_result,
            "safety": {
                "live_trading_enabled": (
                    self.config.LIVE_TRADING_ENABLED
                ),
                "real_broker_enabled": (
                    self.config.REAL_BROKER_ENABLED
                ),
                "place_real_orders": (
                    self.config.PLACE_REAL_ORDERS
                ),
                "paper_only": (
                    self.config.PAPER_ONLY
                ),
                "real_orders_placed": 0,
            },
        }

        self._write_report(report)

        return report

    def _write_report(
        self,
        report: Dict[str, Any],
    ) -> None:

        directory = (
            self.config.REPORT_DIRECTORY
        )

        os.makedirs(
            directory,
            exist_ok=True,
        )

        report_path = os.path.join(
            directory,
            self.config.REPORT_FILENAME,
        )

        audit_path = os.path.join(
            directory,
            self.config.AUDIT_FILENAME,
        )

        with open(
            report_path,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                report,
                handle,
                indent=2,
            )

        with open(
            audit_path,
            "w",
            encoding="utf-8",
        ) as handle:

            for event in self.audit.events:

                handle.write(
                    json.dumps(
                        event,
                        sort_keys=True,
                    )
                    + "\n"
                )

# ============================================================
# PHASE 26 - ROLLBACK ENGINE
# ============================================================

from datetime import datetime
from typing import Dict


class CanaryRollbackEngine:

    def __init__(
        self,
        enabled: bool = True,
    ):

        self.enabled = bool(
            enabled
        )

        self.rollback_triggered = False

        self.reason = ""

    def evaluate(
        self,
        performance: Dict,
        risk: Dict,
        execution: Dict,
        health: Dict,
        safety: Dict,
    ) -> Dict:

        failures = []

        if not performance.get(
            "passed",
            False,
        ):
            failures.append(
                "PERFORMANCE_FAILURE"
            )

        if not risk.get(
            "passed",
            False,
        ):
            failures.append(
                "RISK_FAILURE"
            )

        if not execution.get(
            "passed",
            False,
        ):
            failures.append(
                "EXECUTION_FAILURE"
            )

        if not health.get(
            "passed",
            False,
        ):
            failures.append(
                "HEALTH_FAILURE"
            )

        if not safety.get(
            "passed",
            False,
        ):
            failures.append(
                "SAFETY_FAILURE"
            )

        rollback_required = (
            len(failures) > 0
        )

        if (
            rollback_required
            and self.enabled
        ):

            self.rollback_triggered = True

            self.reason = (
                ",".join(failures)
            )

        return {
            "rollback_required": bool(
                rollback_required
            ),
            "rollback_triggered": bool(
                self.rollback_triggered
            ),
            "reason": self.reason,
            "failure_reasons": failures,
            "timestamp": (
                datetime.utcnow().isoformat()
            ),
        }

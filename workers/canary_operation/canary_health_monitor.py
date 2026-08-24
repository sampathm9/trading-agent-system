from typing import Dict


class CanaryHealthMonitor:

    def evaluate(
        self,
        broker_connected: bool,
        intelligence_healthy: bool,
        position_reconciliation: bool,
        safety_healthy: bool,
        audit_healthy: bool,
    ) -> Dict:

        checks = {
            "broker": bool(
                broker_connected
            ),
            "intelligence": bool(
                intelligence_healthy
            ),
            "position_reconciliation": bool(
                position_reconciliation
            ),
            "safety": bool(
                safety_healthy
            ),
            "audit": bool(
                audit_healthy
            ),
        }

        score = sum(
            1 for value in checks.values()
            if value
        ) / len(checks)

        return {
            "healthy": score >= 0.80,
            "score": round(score, 6),
            "checks": checks,
        }

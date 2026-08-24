from typing import Dict


class CanaryAlertEngine:

    def __init__(self):
        self.alerts = []

    def evaluate(
        self,
        limits: Dict,
        health: Dict,
        safety: Dict,
    ) -> Dict:

        alerts = []

        if not limits["allowed"]:
            alerts.append({
                "type": "LIMIT",
                "reason": limits["reason"],
            })

        if not health["healthy"]:
            alerts.append({
                "type": "HEALTH",
                "reason": "HEALTH_CHECK_FAILED",
            })

        if not safety["allowed"]:
            alerts.append({
                "type": "SAFETY",
                "reason": safety["reason"],
            })

        self.alerts.extend(alerts)

        return {
            "alert_count": len(alerts),
            "alerts": alerts,
            "healthy": len(alerts) == 0,
        }

from typing import Dict


class CanaryReadiness:

    def evaluate(
        self,
        config_safe: bool,
        health_score: float,
        broker_connected: bool,
        reconciliation: bool,
        alerts_clear: bool,
        observation_count: int,
    ) -> Dict:

        checks = {
            "configuration_safe": bool(
                config_safe
            ),
            "health": float(
                health_score
            ) >= 0.80,
            "broker": bool(
                broker_connected
            ),
            "reconciliation": bool(
                reconciliation
            ),
            "alerts_clear": bool(
                alerts_clear
            ),
            "observations": int(
                observation_count
            ) > 0,
        }

        score = (
            sum(
                1 for value in checks.values()
                if value
            )
            / len(checks)
        )

        ready = all(checks.values())

        return {
            "ready": ready,
            "score": round(score, 6),
            "classification": (
                "CANARY_OPERATION_READY"
                if ready
                else "CANARY_OPERATION_BLOCKED"
            ),
            "checks": checks,
        }

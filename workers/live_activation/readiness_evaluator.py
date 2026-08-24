from typing import Dict


class ActivationReadinessEvaluator:

    def evaluate(
        self,
        configuration_valid: bool,
        phase23_ready: bool,
        broker_ready: bool,
        positions_reconciled: bool,
        health_ready: bool,
        canary_ready: bool,
        safety_ready: bool,
    ) -> Dict:

        checks = {
            "configuration": bool(
                configuration_valid
            ),
            "phase23": bool(
                phase23_ready
            ),
            "broker": bool(
                broker_ready
            ),
            "position_reconciliation": bool(
                positions_reconciled
            ),
            "health": bool(
                health_ready
            ),
            "canary_limits": bool(
                canary_ready
            ),
            "safety": bool(
                safety_ready
            ),
        }

        passed = sum(
            1
            for value in checks.values()
            if value
        )

        total = len(checks)

        score = (
            passed / total
            if total
            else 0.0
        )

        ready = (
            score >= 0.90
            and all(checks.values())
        )

        return {
            "ready": ready,
            "score": round(
                score,
                6,
            ),
            "classification": (
                "LIVE_CANARY_READY"
                if ready
                else "NOT_LIVE_CANARY_READY"
            ),
            "checks": checks,
        }

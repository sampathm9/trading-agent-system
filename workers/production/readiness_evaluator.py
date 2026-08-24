from typing import Dict


class Phase20ReadinessEvaluator:

    def evaluate(
        self,
        preflight: Dict,
        safety: Dict,
        health: Dict,
        audit_events: int,
    ) -> Dict:

        checks = {
            "preflight": bool(
                preflight.get(
                    "passed",
                    False,
                )
            ),
            "runtime_safety": bool(
                safety.get(
                    "allowed",
                    False,
                )
            ),
            "health": bool(
                health
                and all(
                    item.get(
                        "healthy",
                        False,
                    )
                    for item in health.values()
                )
            ),
            "audit_logging": (
                audit_events > 0
            ),
            "real_trading_disabled": True,
        }

        passed_count = sum(
            1
            for value in checks.values()
            if value
        )

        total = len(checks)

        score = (
            passed_count / total
            if total
            else 0.0
        )

        ready = (
            score == 1.0
            and checks[
                "real_trading_disabled"
            ]
        )

        return {
            "ready": ready,
            "score": round(
                score,
                6,
            ),
            "classification": (
                "PAPER_PRODUCTION_READY"
                if ready
                else "NOT_READY"
            ),
            "checks": checks,
        }

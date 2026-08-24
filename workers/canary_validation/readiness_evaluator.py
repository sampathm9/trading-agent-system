# ============================================================
# PHASE 26 - READINESS EVALUATOR
# ============================================================

from typing import Dict


class CanaryReadinessEvaluator:

    def __init__(
        self,
        minimum_score: float = 0.80,
    ):

        self.minimum_score = float(
            minimum_score
        )

    def evaluate(
        self,
        checks: Dict,
    ) -> Dict:

        values = []

        for value in checks.values():

            values.append(
                bool(value)
            )

        score = (
            sum(values) / len(values)
            if values
            else 0.0
        )

        passed = (
            score
            >= self.minimum_score
        )

        return {
            "ready": bool(passed),
            "score": round(
                score,
                6,
            ),
            "classification": (
                "CANARY_CONTINUE"
                if passed
                else "CANARY_ROLLBACK_REQUIRED"
            ),
            "checks": checks,
        }

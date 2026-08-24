import json
from pathlib import Path
from typing import Dict


class Phase25ReadinessEvaluator:

    def evaluate(
        self,
        result: Dict,
    ) -> Dict:

        safety = result.get(
            "safety",
            {},
        )

        health = result.get(
            "health",
            {},
        )

        readiness = result.get(
            "readiness",
            {},
        )

        checks = {
            "safety": bool(
                safety.get("allowed")
            ),
            "health": bool(
                health.get("healthy")
            ),
            "readiness": bool(
                readiness.get("ready")
            ),
            "real_orders_zero": (
                result.get(
                    "real_orders_placed",
                    1,
                )
                == 0
            ),
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
                "CONTROLLED_CANARY_READY"
                if ready
                else "CONTROLLED_CANARY_BLOCKED"
            ),
            "checks": checks,
        }

    def save(
        self,
        result: Dict,
        path: str,
    ):

        target = Path(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

# ============================================================
# PHASE 26 - HEALTH VALIDATOR
# ============================================================

from typing import Dict


class CanaryHealthValidator:

    def __init__(
        self,
        max_health_failures: int = 0,
    ):

        self.max_health_failures = int(
            max_health_failures
        )

    def validate(
        self,
        health: Dict,
    ) -> Dict:

        failures = int(
            health.get(
                "failures",
                0,
            )
        )

        healthy = bool(
            health.get(
                "healthy",
                False,
            )
        )

        passed = (
            healthy
            and failures
            <= self.max_health_failures
        )

        return {
            "passed": bool(passed),
            "healthy": healthy,
            "failures": failures,
            "checks": {
                "healthy": healthy,
                "failure_limit": (
                    failures
                    <= self.max_health_failures
                ),
            },
        }

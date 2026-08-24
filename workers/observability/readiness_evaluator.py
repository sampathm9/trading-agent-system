from typing import Dict, Any


class ObservabilityReadiness:

    def __init__(
        self,
        minimum_components: int = 5,
        minimum_healthy_components: int = 5,
        maximum_critical_incidents: int = 0,
    ):

        self.minimum_components = int(
            minimum_components
        )

        self.minimum_healthy_components = int(
            minimum_healthy_components
        )

        self.maximum_critical_incidents = int(
            maximum_critical_incidents
        )

    def evaluate(
        self,
        health: Dict[str, Any],
        incidents: Dict[str, Any],
        safety: Dict[str, Any],
    ) -> Dict[str, Any]:

        component_count = int(
            health.get("required_count", 0)
        )

        healthy_count = int(
            health.get("healthy_count", 0)
        )

        critical_count = int(
            incidents.get("critical_count", 0)
        )

        checks = {
            "minimum_components":
                component_count >= self.minimum_components,

            "minimum_healthy_components":
                healthy_count >=
                self.minimum_healthy_components,

            "critical_incidents":
                critical_count <=
                self.maximum_critical_incidents,

            "safety":
                bool(safety.get("safe", False)),
        }

        passed = sum(
            1
            for value in checks.values()
            if value
        )

        score = (
            passed / len(checks)
            if checks
            else 0.0
        )

        ready = all(checks.values())

        return {
            "ready": ready,
            "classification":
                (
                    "OBSERVABILITY_READY"
                    if ready
                    else "OBSERVABILITY_NOT_READY"
                ),
            "score": score,
            "checks": checks,
        }

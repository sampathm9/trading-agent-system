from typing import Dict, Any, List

from workers.observability.incident_model import (
    Incident,
    utc_now,
)


class IncidentDetector:

    def __init__(self):
        self.incidents: List[Incident] = []
        self.counter = 0

    def detect_component_failure(
        self,
        component: str,
        healthy: bool,
        details: Dict[str, Any] | None = None,
    ) -> Incident | None:

        if healthy:
            return None

        self.counter += 1

        incident = Incident(
            incident_id=f"INC-{self.counter:05d}",
            severity="CRITICAL",
            component=component,
            incident_type="COMPONENT_FAILURE",
            message=(
                f"Component '{component}' reported unhealthy"
            ),
            timestamp=utc_now(),
        )

        self.incidents.append(incident)

        return incident

    def detect_safety_violation(
        self,
        safety: Dict[str, Any],
    ) -> Incident | None:

        if (
            safety.get("live_trading_enabled") is False
            and safety.get("real_broker_enabled") is False
            and safety.get("place_real_orders") is False
        ):
            return None

        self.counter += 1

        incident = Incident(
            incident_id=f"INC-{self.counter:05d}",
            severity="CRITICAL",
            component="safety",
            incident_type="SAFETY_VIOLATION",
            message="Unsafe live trading configuration detected",
            timestamp=utc_now(),
        )

        self.incidents.append(incident)

        return incident

    def critical_count(self) -> int:
        return sum(
            1
            for item in self.incidents
            if item.severity == "CRITICAL"
        )

    def snapshot(self) -> List[Dict[str, Any]]:
        return [
            item.to_dict()
            for item in self.incidents
        ]

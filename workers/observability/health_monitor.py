from datetime import datetime, timezone
from typing import Dict, Any, Optional


class ObservabilityHealthMonitor:

    REQUIRED_COMPONENTS = [
        "historical_data",
        "paper_broker",
        "intelligence",
        "runtime",
        "safety",
        "audit",
    ]

    def __init__(self):
        self.status = {}
        self.last_heartbeat = {}

    def heartbeat(
        self,
        component: str,
        healthy: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        timestamp = datetime.now(timezone.utc).isoformat()

        self.status[component] = {
            "healthy": bool(healthy),
            "timestamp": timestamp,
            "details": details or {},
        }

        self.last_heartbeat[component] = timestamp

        return self.status[component]

    def component_health(self, component: str) -> bool:
        item = self.status.get(component)

        if not item:
            return False

        return bool(item.get("healthy", False))

    def healthy_count(self) -> int:
        return sum(
            1
            for component in self.REQUIRED_COMPONENTS
            if self.component_health(component)
        )

    def all_required_healthy(self) -> bool:
        return all(
            self.component_health(component)
            for component in self.REQUIRED_COMPONENTS
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "components": dict(self.status),
            "healthy_count": self.healthy_count(),
            "required_count": len(self.REQUIRED_COMPONENTS),
            "all_required_healthy": self.all_required_healthy(),
        }

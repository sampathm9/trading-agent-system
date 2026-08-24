import time
from typing import Dict


class Phase20HealthMonitor:

    def __init__(
        self,
        heartbeat_timeout_seconds: int = 60,
    ):

        self.timeout = int(
            heartbeat_timeout_seconds
        )

        self.last_heartbeat = None

        self.components = {}

    def heartbeat(
        self,
        component: str,
    ):

        self.last_heartbeat = time.time()

        self.components[
            component
        ] = {
            "healthy": True,
            "timestamp": self.last_heartbeat,
        }

    def check_component(
        self,
        component: str,
    ) -> Dict:

        if component not in self.components:

            return {
                "healthy": False,
                "reason": (
                    "No heartbeat received."
                ),
            }

        timestamp = self.components[
            component
        ]["timestamp"]

        age = (
            time.time()
            - timestamp
        )

        healthy = (
            age <= self.timeout
        )

        return {
            "healthy": healthy,
            "age_seconds": round(
                age,
                6,
            ),
        }

    def snapshot(self) -> Dict:

        result = {}

        for component in self.components:

            result[component] = (
                self.check_component(
                    component
                )
            )

        return result

    def all_healthy(self) -> bool:

        snapshot = self.snapshot()

        return bool(snapshot) and all(
            item["healthy"]
            for item in snapshot.values()
        )

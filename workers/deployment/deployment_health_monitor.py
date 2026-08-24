from typing import Dict


class DeploymentHealthMonitor:

    def check(
        self,
        broker,
        intelligence_worker,
    ) -> Dict:

        checks = {}

        try:
            checks["broker_connected"] = bool(
                broker.is_connected()
            )
        except Exception:
            checks["broker_connected"] = False

        checks["intelligence_available"] = (
            intelligence_worker is not None
        )

        healthy = all(checks.values())

        return {
            "healthy": healthy,
            "checks": checks,
        }

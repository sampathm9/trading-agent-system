class RuntimeHealthMonitor:

    def __init__(self, registry):
        self.registry = registry

    def check(self):

        report = self.registry.health_report()

        healthy = all(
            item["healthy"]
            for item in report.values()
        )

        return {
            "healthy": healthy,
            "components": report,
        }

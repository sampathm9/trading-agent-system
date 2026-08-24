class RuntimePreflight:

    def __init__(
        self,
        safety,
        registry,
    ):
        self.safety = safety
        self.registry = registry

    def validate(self):

        safety = self.safety.validate()

        components_registered = (
            self.registry.all_registered()
        )

        components_healthy = (
            self.registry.all_healthy()
        )

        passed = (
            safety["safe"]
            and components_registered
            and components_healthy
        )

        return {
            "passed": passed,
            "safety": safety,
            "components_registered":
                components_registered,
            "components_healthy":
                components_healthy,
            "component_health":
                self.registry.health_report(),
        }

class RuntimeComponentRegistry:

    def __init__(self, required_components):
        self.required = list(required_components)
        self.components = {}

    def register(self, name, healthy=True, details=None):

        self.components[name] = {
            "healthy": bool(healthy),
            "details": details or {},
        }

    def all_registered(self):

        return all(
            name in self.components
            for name in self.required
        )

    def all_healthy(self):

        if not self.all_registered():
            return False

        return all(
            self.components[name]["healthy"]
            for name in self.required
        )

    def health_report(self):

        return {
            name: self.components.get(
                name,
                {
                    "healthy": False,
                    "details": {
                        "reason": "not registered"
                    },
                },
            )
            for name in self.required
        }

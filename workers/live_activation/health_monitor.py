from typing import Dict


class LiveHealthMonitor:

    def __init__(
        self,
        max_errors: int = 3,
    ):

        self.max_errors = int(
            max_errors
        )

        self.errors = 0
        self.checks = 0

    def check(
        self,
        broker,
        intelligence=None,
    ) -> Dict:

        self.checks += 1

        failures = []

        if broker is None:

            failures.append(
                "Broker unavailable"
            )

        else:

            try:

                if hasattr(
                    broker,
                    "is_connected",
                ):

                    connected = (
                        broker.is_connected()
                    )

                    if not connected:
                        failures.append(
                            "Broker disconnected"
                        )

            except Exception as exc:

                failures.append(
                    f"Broker health error: {exc}"
                )

        if intelligence is None:

            failures.append(
                "Intelligence worker unavailable"
            )

        if failures:

            self.errors += 1

        healthy = (
            len(failures) == 0
            and self.errors <= self.max_errors
        )

        return {
            "healthy": healthy,
            "checks": self.checks,
            "errors": self.errors,
            "failures": failures,
        }

    def reset(self):

        self.errors = 0

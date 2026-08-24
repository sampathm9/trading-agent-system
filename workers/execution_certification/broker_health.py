from typing import Dict


class Phase21BrokerHealth:

    def __init__(self):

        self.last_status = None

    def check(
        self,
        broker,
    ) -> Dict:

        if broker is None:

            self.last_status = {
                "healthy": False,
                "reason": (
                    "Broker is unavailable."
                ),
            }

            return self.last_status

        try:

            connected = bool(
                broker.is_connected()
            )

        except Exception as exc:

            self.last_status = {
                "healthy": False,
                "reason": str(exc),
            }

            return self.last_status

        self.last_status = {
            "healthy": connected,
            "reason": (
                "Broker connected."
                if connected
                else "Broker disconnected."
            ),
        }

        return self.last_status

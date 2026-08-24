from typing import Dict, Any


class ObservabilitySafety:

    def __init__(
        self,
        live_trading_enabled: bool = False,
        real_broker_enabled: bool = False,
        place_real_orders: bool = False,
    ):

        self.live_trading_enabled = bool(
            live_trading_enabled
        )

        self.real_broker_enabled = bool(
            real_broker_enabled
        )

        self.place_real_orders = bool(
            place_real_orders
        )

        self.emergency_shutdown = False

    def validate(self) -> Dict[str, Any]:

        safe = (
            not self.live_trading_enabled
            and not self.real_broker_enabled
            and not self.place_real_orders
        )

        if self.emergency_shutdown:
            safe = False

        return {
            "safe": safe,
            "live_trading_enabled":
                self.live_trading_enabled,
            "real_broker_enabled":
                self.real_broker_enabled,
            "place_real_orders":
                self.place_real_orders,
            "emergency_shutdown":
                self.emergency_shutdown,
        }

    def activate_emergency_shutdown(self) -> None:
        self.emergency_shutdown = True

    def recover_emergency_shutdown(self) -> None:
        self.emergency_shutdown = False

    def execution_allowed(self) -> bool:
        state = self.validate()
        return bool(state["safe"])

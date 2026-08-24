from typing import Dict

from config.phase23_config import (
    LIVE_TRADING_ENABLED,
    PLACE_REAL_ORDERS,
    REAL_BROKER_ENABLED,
    SHADOW_MODE,
)


class Phase23ShadowSafety:

    def validate(self) -> Dict:

        checks = {
            "shadow_mode": SHADOW_MODE is True,
            "live_trading_disabled": (
                LIVE_TRADING_ENABLED is False
            ),
            "real_broker_disabled": (
                REAL_BROKER_ENABLED is False
            ),
            "real_orders_disabled": (
                PLACE_REAL_ORDERS is False
            ),
        }

        return {
            "allowed": all(checks.values()),
            "checks": checks,
        }

    def assert_safe(self):

        result = self.validate()

        if not result["allowed"]:

            raise RuntimeError(
                "PHASE 23 SAFETY FAILURE: "
                "shadow trading safety configuration "
                "does not prohibit real orders."
            )

        return True

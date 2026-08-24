from typing import Dict


class CanarySafety:

    def __init__(self):
        self.emergency_shutdown = False

    def shutdown(self):
        self.emergency_shutdown = True

    def recover(self):
        self.emergency_shutdown = False

    def validate_configuration(
        self,
        config,
    ) -> Dict:

        checks = {
            "canary_mode": bool(
                config.CANARY_MODE
            ),
            "paper_only": bool(
                config.PAPER_ONLY
            ),
            "shadow_mode": bool(
                config.SHADOW_MODE
            ),
            "live_trading_disabled": (
                not bool(
                    config.LIVE_TRADING_ENABLED
                )
            ),
            "real_broker_disabled": (
                not bool(
                    config.REAL_BROKER_ENABLED
                )
            ),
            "real_orders_disabled": (
                not bool(
                    config.PLACE_REAL_ORDERS
                )
            ),
        }

        return {
            "allowed": all(checks.values()),
            "checks": checks,
        }

    def can_operate(
        self,
        config,
    ) -> Dict:

        validation = self.validate_configuration(
            config
        )

        if self.emergency_shutdown:
            return {
                "allowed": False,
                "reason": "EMERGENCY_SHUTDOWN_ACTIVE",
                "checks": validation["checks"],
            }

        if not validation["allowed"]:
            return {
                "allowed": False,
                "reason": "SAFETY_CONFIGURATION_FAILED",
                "checks": validation["checks"],
            }

        return {
            "allowed": True,
            "reason": "CANARY_SAFETY_OK",
            "checks": validation["checks"],
        }

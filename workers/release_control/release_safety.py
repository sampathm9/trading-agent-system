from typing import Dict


class ReleaseSafetyController:

    def __init__(self, config):
        self.config = config
        self.emergency_stop = bool(
            config.EMERGENCY_STOP_DEFAULT
        )

    def validate(self) -> Dict:

        checks = {
            "paper_mode": self.config.PAPER_MODE is True,
            "shadow_mode": self.config.SHADOW_MODE is True,
            "live_trading_disabled": (
                self.config.LIVE_TRADING_ENABLED is False
            ),
            "real_broker_disabled": (
                self.config.REAL_BROKER_ENABLED is False
            ),
            "real_orders_disabled": (
                self.config.PLACE_REAL_ORDERS is False
            ),
            "automatic_live_activation_disabled": (
                self.config.ALLOW_AUTOMATIC_LIVE_ACTIVATION is False
            ),
            "human_approval_required": (
                self.config.REQUIRE_HUMAN_RELEASE_APPROVAL is True
            ),
        }

        return {
            "passed": all(checks.values()),
            "checks": checks,
        }

    def activate_emergency_stop(self):
        self.emergency_stop = True

    def recover_emergency_stop(self):
        self.emergency_stop = False

    def execution_allowed(self) -> bool:

        if self.emergency_stop:
            return False

        result = self.validate()

        return bool(result["passed"])

# ============================================================
# PHASE 26 - SAFETY VALIDATOR
# ============================================================

from typing import Dict


class CanarySafetyValidator:

    REQUIRED = {
        "canary_mode": True,
        "live_trading_enabled": False,
        "real_broker_enabled": False,
        "place_real_orders": False,
        "auto_live_activation_enabled": False,
    }

    def validate(
        self,
        safety: Dict,
    ) -> Dict:

        checks = {}

        for key, expected in self.REQUIRED.items():

            checks[key] = (
                safety.get(key)
                == expected
            )

        passed = all(
            checks.values()
        )

        return {
            "passed": bool(passed),
            "checks": checks,
            "real_orders_allowed": False,
        }

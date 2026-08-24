from typing import Dict

from config.phase22_config import (
    LIVE_CONFIRMATION_REQUIRED,
    LIVE_TRADING_ENABLED,
    REAL_BROKER_ENABLED,
)


class LiveTradingGate:

    def __init__(self):

        self.explicit_confirmation = False
        self.kill_switch = False

    def confirm_live(self):

        self.explicit_confirmation = True

    def activate_kill_switch(self):

        self.kill_switch = True

    def reset_kill_switch(self):

        self.kill_switch = False

    def evaluate(self) -> Dict:

        reasons = []

        if not LIVE_TRADING_ENABLED:
            reasons.append(
                "Live trading disabled by configuration"
            )

        if not REAL_BROKER_ENABLED:
            reasons.append(
                "Real broker disabled by configuration"
            )

        if LIVE_CONFIRMATION_REQUIRED:
            if not self.explicit_confirmation:
                reasons.append(
                    "Explicit live confirmation missing"
                )

        if self.kill_switch:
            reasons.append(
                "Emergency kill switch active"
            )

        allowed = len(reasons) == 0

        return {
            "allowed": allowed,
            "reasons": reasons,
            "live_trading_enabled": LIVE_TRADING_ENABLED,
            "real_broker_enabled": REAL_BROKER_ENABLED,
            "explicit_confirmation": (
                self.explicit_confirmation
            ),
            "kill_switch": self.kill_switch,
        }

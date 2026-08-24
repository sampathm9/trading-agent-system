from typing import Dict


class ProductionSessionController:

    def __init__(
        self,
        config,
        safety_controller,
    ):
        self.config = config
        self.safety = safety_controller

        self.running = False
        self.trade_count = 0
        self.realized_pnl = 0.0
        self.consecutive_losses = 0

    def start(self) -> Dict:

        if not self.safety.execution_allowed():
            return {
                "started": False,
                "reason": "Safety gate blocked session",
            }

        self.running = True

        return {
            "started": True,
            "mode": (
                "PAPER"
                if self.config.PAPER_MODE
                else "LIVE"
            ),
        }

    def can_trade(self) -> Dict:

        if not self.running:
            return {
                "allowed": False,
                "reason": "Session is not running",
            }

        if self.trade_count >= self.config.MAX_SESSION_TRADES:
            return {
                "allowed": False,
                "reason": "Maximum session trades reached",
            }

        if self.realized_pnl <= -abs(
            self.config.MAX_SESSION_LOSS
        ):
            return {
                "allowed": False,
                "reason": "Maximum session loss reached",
            }

        if (
            self.consecutive_losses
            >= self.config.MAX_CONSECUTIVE_LOSSES
        ):
            return {
                "allowed": False,
                "reason": "Maximum consecutive losses reached",
            }

        if not self.safety.execution_allowed():
            return {
                "allowed": False,
                "reason": "Safety controller blocked execution",
            }

        return {
            "allowed": True,
            "reason": "Session limits passed",
        }

    def register_trade(self, pnl: float):

        self.trade_count += 1
        self.realized_pnl += float(pnl)

        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

    def stop(self):

        self.running = False

from typing import Dict, Optional

from config.phase14_config import (
    MAX_TRADES_PER_SESSION,
    MAX_QUANTITY,
    PAPER_ONLY,
)


class SafetyGateway:

    def __init__(self):

        self.trade_count = 0
        self.paper_only = PAPER_ONLY

    def validate(
        self,
        action: str,
        quantity: int,
        can_trade: bool,
    ) -> Dict:

        action = str(action).upper()

        if not self.paper_only:
            return {
                "approved": False,
                "reason": "Phase 14 requires paper-only mode",
            }

        if not can_trade:
            return {
                "approved": False,
                "reason": "Trading session does not permit orders",
            }

        if action not in {"BUY", "SELL"}:
            return {
                "approved": False,
                "reason": "Action is not executable",
            }

        if quantity <= 0:
            return {
                "approved": False,
                "reason": "Quantity must be positive",
            }

        if quantity > MAX_QUANTITY:
            return {
                "approved": False,
                "reason": "Quantity exceeds Phase 14 limit",
            }

        if self.trade_count >= MAX_TRADES_PER_SESSION:
            return {
                "approved": False,
                "reason": "Maximum session trades reached",
            }

        return {
            "approved": True,
            "reason": "Safety gateway approved",
        }

    def record_trade(self):
        self.trade_count += 1

    def reset(self):
        self.trade_count = 0

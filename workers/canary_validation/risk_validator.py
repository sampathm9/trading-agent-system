# ============================================================
# PHASE 26 - RISK VALIDATOR
# ============================================================

from typing import Dict, List


class CanaryRiskValidator:

    def __init__(
        self,
        max_canary_trades: int,
        max_consecutive_losses: int,
    ):

        self.max_canary_trades = int(
            max_canary_trades
        )

        self.max_consecutive_losses = int(
            max_consecutive_losses
        )

    def validate(
        self,
        trades: List[Dict],
        consecutive_losses: int,
    ) -> Dict:

        trade_count = len(trades)

        trade_limit_pass = (
            trade_count
            <= self.max_canary_trades
        )

        loss_limit_pass = (
            int(consecutive_losses)
            <= self.max_consecutive_losses
        )

        passed = (
            trade_limit_pass
            and loss_limit_pass
        )

        return {
            "passed": bool(passed),
            "trade_count": trade_count,
            "consecutive_losses": int(
                consecutive_losses
            ),
            "checks": {
                "trade_limit": bool(
                    trade_limit_pass
                ),
                "consecutive_losses": bool(
                    loss_limit_pass
                ),
            },
        }

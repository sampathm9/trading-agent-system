from typing import Dict


class CanaryLimits:

    def __init__(
        self,
        max_trades: int,
        max_consecutive_losses: int,
        max_daily_loss: float,
        max_daily_profit: float,
        max_position_quantity: int,
    ):
        self.max_trades = int(max_trades)
        self.max_consecutive_losses = int(
            max_consecutive_losses
        )
        self.max_daily_loss = float(max_daily_loss)
        self.max_daily_profit = float(max_daily_profit)
        self.max_position_quantity = int(
            max_position_quantity
        )

    def check(
        self,
        total_trades: int,
        realized_pnl: float,
        consecutive_losses: int,
        position_quantity: int,
    ) -> Dict:

        total_trades = int(total_trades)
        realized_pnl = float(realized_pnl)
        consecutive_losses = int(
            consecutive_losses
        )
        position_quantity = int(position_quantity)

        if total_trades >= self.max_trades:
            return {
                "allowed": False,
                "reason": "MAX_CANARY_TRADES_REACHED",
            }

        if (
            realized_pnl
            <= -self.max_daily_loss
        ):
            return {
                "allowed": False,
                "reason": "MAX_DAILY_LOSS_REACHED",
            }

        if (
            realized_pnl
            >= self.max_daily_profit
        ):
            return {
                "allowed": False,
                "reason": "MAX_DAILY_PROFIT_REACHED",
            }

        if (
            consecutive_losses
            >= self.max_consecutive_losses
        ):
            return {
                "allowed": False,
                "reason": "MAX_CONSECUTIVE_LOSSES_REACHED",
            }

        if (
            abs(position_quantity)
            > self.max_position_quantity
        ):
            return {
                "allowed": False,
                "reason": "MAX_POSITION_QUANTITY_EXCEEDED",
            }

        return {
            "allowed": True,
            "reason": "CANARY_LIMITS_OK",
        }

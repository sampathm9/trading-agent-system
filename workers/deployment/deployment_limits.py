from typing import Dict


class DeploymentLimits:

    def __init__(
        self,
        max_order_quantity: int,
        max_daily_trades: int,
        max_daily_loss: float,
    ):

        self.max_order_quantity = int(
            max_order_quantity
        )

        self.max_daily_trades = int(
            max_daily_trades
        )

        self.max_daily_loss = float(
            max_daily_loss
        )

    def validate_order(
        self,
        quantity: int,
    ) -> Dict:

        quantity = int(quantity)

        if quantity <= 0:
            return {
                "allowed": False,
                "reason": "Quantity must be greater than zero",
            }

        if quantity > self.max_order_quantity:
            return {
                "allowed": False,
                "reason": (
                    "Order quantity exceeds deployment limit"
                ),
            }

        return {
            "allowed": True,
            "reason": "Order quantity within limit",
        }

    def validate_session(
        self,
        total_trades: int,
        realized_pnl: float,
    ) -> Dict:

        if total_trades >= self.max_daily_trades:
            return {
                "allowed": False,
                "reason": "Maximum daily trades reached",
            }

        if realized_pnl <= -self.max_daily_loss:
            return {
                "allowed": False,
                "reason": "Maximum daily loss reached",
            }

        return {
            "allowed": True,
            "reason": "Session within deployment limits",
        }

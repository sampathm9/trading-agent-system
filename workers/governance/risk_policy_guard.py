from typing import Any, Dict


class RiskPolicyGuard:

    def __init__(
        self,
        max_order_quantity: int,
        max_daily_trades: int,
        max_daily_loss: float,
        max_consecutive_losses: int,
    ):

        self.max_order_quantity = int(max_order_quantity)
        self.max_daily_trades = int(max_daily_trades)
        self.max_daily_loss = float(max_daily_loss)
        self.max_consecutive_losses = int(
            max_consecutive_losses
        )

    def validate(
        self,
        quantity: int,
        daily_trades: int,
        daily_loss: float,
        consecutive_losses: int,
    ) -> Dict[str, Any]:

        checks = {
            "quantity": (
                int(quantity) <= self.max_order_quantity
            ),
            "daily_trades": (
                int(daily_trades) <= self.max_daily_trades
            ),
            "daily_loss": (
                float(daily_loss) <= self.max_daily_loss
            ),
            "consecutive_losses": (
                int(consecutive_losses)
                <= self.max_consecutive_losses
            ),
        }

        errors = []

        if not checks["quantity"]:
            errors.append("Order quantity exceeds limit.")

        if not checks["daily_trades"]:
            errors.append("Daily trade count exceeds limit.")

        if not checks["daily_loss"]:
            errors.append("Daily loss exceeds limit.")

        if not checks["consecutive_losses"]:
            errors.append(
                "Consecutive loss limit exceeded."
            )

        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
            "limits": {
                "max_order_quantity": self.max_order_quantity,
                "max_daily_trades": self.max_daily_trades,
                "max_daily_loss": self.max_daily_loss,
                "max_consecutive_losses": (
                    self.max_consecutive_losses
                ),
            },
        }

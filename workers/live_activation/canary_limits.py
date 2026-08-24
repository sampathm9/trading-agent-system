from typing import Dict


class CanaryLimitManager:

    def __init__(
        self,
        max_orders: int,
        max_quantity: int,
        max_daily_loss: float,
        max_consecutive_losses: int,
        max_open_positions: int,
    ):

        self.max_orders = int(max_orders)
        self.max_quantity = int(max_quantity)
        self.max_daily_loss = float(max_daily_loss)
        self.max_consecutive_losses = int(
            max_consecutive_losses
        )
        self.max_open_positions = int(
            max_open_positions
        )

    def evaluate(
        self,
        orders: int,
        quantity: int,
        daily_loss: float,
        consecutive_losses: int,
        open_positions: int,
    ) -> Dict:

        failures = []

        if orders > self.max_orders:
            failures.append(
                "Maximum canary orders exceeded"
            )

        if quantity > self.max_quantity:
            failures.append(
                "Maximum canary quantity exceeded"
            )

        if daily_loss < -abs(
            self.max_daily_loss
        ):
            failures.append(
                "Maximum daily loss exceeded"
            )

        if consecutive_losses > (
            self.max_consecutive_losses
        ):
            failures.append(
                "Maximum consecutive losses exceeded"
            )

        if open_positions > (
            self.max_open_positions
        ):
            failures.append(
                "Maximum open positions exceeded"
            )

        return {
            "allowed": len(failures) == 0,
            "failures": failures,
        }

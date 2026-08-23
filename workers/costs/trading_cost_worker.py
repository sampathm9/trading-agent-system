class TradingCostWorker:

    def __init__(
        self,
        brokerage_per_order=0.0,
        slippage_pct=0.0,
        transaction_cost_pct=0.0,
        other_cost_per_order=0.0
    ):

        self.brokerage_per_order = float(
            brokerage_per_order
        )

        self.slippage_pct = float(
            slippage_pct
        )

        self.transaction_cost_pct = float(
            transaction_cost_pct
        )

        self.other_cost_per_order = float(
            other_cost_per_order
        )

    def apply_slippage(
        self,
        price,
        side
    ):

        price = float(price)

        if side == "BUY":

            return price * (
                1 + self.slippage_pct
            )

        if side == "SELL":

            return price * (
                1 - self.slippage_pct
            )

        return price

    def calculate_trade_cost(
        self,
        price,
        quantity
    ):

        turnover = (
            float(price)
            * int(quantity)
        )

        transaction_cost = (
            turnover
            * self.transaction_cost_pct
        )

        return (
            self.brokerage_per_order
            + transaction_cost
            + self.other_cost_per_order
        )

    def calculate_trade(
        self,
        entry_price,
        exit_price,
        quantity
    ):

        entry_price = float(entry_price)
        exit_price = float(exit_price)
        quantity = int(quantity)

        gross_pnl = (
            exit_price - entry_price
        ) * quantity

        entry_cost = self.calculate_trade_cost(
            entry_price,
            quantity
        )

        exit_cost = self.calculate_trade_cost(
            exit_price,
            quantity
        )

        total_cost = (
            entry_cost
            + exit_cost
        )

        net_pnl = (
            gross_pnl
            - total_cost
        )

        return {
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "gross_pnl": round(
                gross_pnl,
                4
            ),
            "entry_cost": round(
                entry_cost,
                4
            ),
            "exit_cost": round(
                exit_cost,
                4
            ),
            "total_cost": round(
                total_cost,
                4
            ),
            "net_pnl": round(
                net_pnl,
                4
            )
        }
class ExitAgent:

    def __init__(
        self,
        stop_loss_percent=0.02,
        target_percent=0.04
    ):
        self.stop_loss_percent = stop_loss_percent
        self.target_percent = target_percent

    def evaluate(
        self,
        entry_price,
        current_price,
        side,
        strategy_exit=False,
        market_regime="NORMAL",
        force_exit=False
    ):

        if force_exit:
            return {
                "exit": True,
                "reason": "End of trading session"
            }

        if strategy_exit:
            return {
                "exit": True,
                "reason": "Strategy exit signal"
            }

        if market_regime == "DANGEROUS":
            return {
                "exit": True,
                "reason": "Dangerous market regime"
            }

        if side == "BUY":

            stop_price = (
                entry_price
                * (1 - self.stop_loss_percent)
            )

            target_price = (
                entry_price
                * (1 + self.target_percent)
            )

            if current_price <= stop_price:
                return {
                    "exit": True,
                    "reason": "Stop loss reached",
                    "exit_price": current_price
                }

            if current_price >= target_price:
                return {
                    "exit": True,
                    "reason": "Target reached",
                    "exit_price": current_price
                }

        elif side == "SELL":

            stop_price = (
                entry_price
                * (1 + self.stop_loss_percent)
            )

            target_price = (
                entry_price
                * (1 - self.target_percent)
            )

            if current_price >= stop_price:
                return {
                    "exit": True,
                    "reason": "Stop loss reached",
                    "exit_price": current_price
                }

            if current_price <= target_price:
                return {
                    "exit": True,
                    "reason": "Target reached",
                    "exit_price": current_price
                }

        return {
            "exit": False,
            "reason": "Position remains open"
        }
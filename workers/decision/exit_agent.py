class ExitAgent:

    def evaluate(
        self,
        current_price,
        entry_price,
        side,
        strategy_exit=False,
        market_regime="UNKNOWN",
        force_exit=False
    ):

        if force_exit:
            return {
                "action": "EXIT",
                "reason": "Force exit requested"
            }

        if strategy_exit:
            return {
                "action": "EXIT",
                "reason": "Strategy exit signal"
            }

        if side == "BUY" and market_regime == "BEARISH":
            return {
                "action": "EXIT",
                "reason": "Market changed to bearish"
            }

        if side == "SELL" and market_regime == "BULLISH":
            return {
                "action": "EXIT",
                "reason": "Market changed to bullish"
            }

        return {
            "action": "HOLD",
            "reason": "No exit condition"
        }
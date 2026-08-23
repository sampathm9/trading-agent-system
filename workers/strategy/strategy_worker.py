class StrategyWorker:

    def decide(self, trend):

        if trend == "BULLISH":
            return "BUY"

        elif trend == "BEARISH":
            return "SELL"

        elif trend == "SIDEWAYS":
            return "HOLD"

        return "NO_TRADE"
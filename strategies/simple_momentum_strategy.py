class SimpleMomentumStrategy:

    name = "Simple Momentum"

    def generate_signal(self, previous_close, current_close):

        if current_close > previous_close:
            return "BUY"

        if current_close < previous_close:
            return "SELL"

        return "HOLD"
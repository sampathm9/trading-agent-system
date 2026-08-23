class IndicatorWorker:

    def sma(self, values, period):

        if period <= 0:
            raise ValueError("period must be greater than zero")

        if len(values) < period:
            return None

        window = values[-period:]

        return sum(
            float(value)
            for value in window
        ) / period

    def ema(self, values, period):

        if period <= 0:
            raise ValueError("period must be greater than zero")

        if len(values) < period:
            return None

        values = [
            float(value)
            for value in values
        ]

        multiplier = 2.0 / (period + 1)

        ema_value = sum(
            values[:period]
        ) / period

        for value in values[period:]:

            ema_value = (
                (value - ema_value)
                * multiplier
            ) + ema_value

        return ema_value

    def returns(self, values):

        if len(values) < 2:
            return []

        result = []

        for index in range(1, len(values)):

            previous = float(
                values[index - 1]
            )

            current = float(
                values[index]
            )

            if previous == 0:
                result.append(0.0)
                continue

            result.append(
                (current - previous)
                / previous
            )

        return result

    def momentum(
        self,
        values,
        period=5
    ):

        if period <= 0:
            raise ValueError(
                "period must be greater than zero"
            )

        if len(values) <= period:
            return None

        previous = float(
            values[-period - 1]
        )

        current = float(
            values[-1]
        )

        if previous == 0:
            return 0.0

        return (
            (current - previous)
            / previous
        )

    def calculate(
        self,
        candles,
        short_period=5,
        long_period=10,
        momentum_period=5
    ):

        if not candles:
            return {
                "status": "NO_DATA"
            }

        closes = [
            float(candle["close"])
            for candle in candles
        ]

        short_sma = self.sma(
            closes,
            short_period
        )

        long_sma = self.sma(
            closes,
            long_period
        )

        momentum = self.momentum(
            closes,
            momentum_period
        )

        latest_price = closes[-1]

        return {
            "status": "COMPLETED",
            "latest_price": latest_price,
            "short_sma": short_sma,
            "long_sma": long_sma,
            "momentum": momentum,
            "candle_count": len(candles),
        }
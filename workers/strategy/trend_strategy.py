from workers.strategy.indicator_worker import (
    IndicatorWorker
)


class TrendStrategy:

    def __init__(
        self,
        indicator_worker=None
    ):

        self.indicators = (
            indicator_worker
            or IndicatorWorker()
        )

    def analyze(
        self,
        candles,
        short_period=5,
        long_period=10,
        momentum_period=5,
    ):

        minimum_candles = max(
            long_period,
            momentum_period + 1
        )

        if len(candles) < minimum_candles:

            return {
                "status": "INSUFFICIENT_DATA",
                "trend": "NEUTRAL",
                "confidence": 0.0,
                "reason": "NOT_ENOUGH_CANDLES",
                "required_candles": minimum_candles,
                "available_candles": len(candles),
            }

        indicators = self.indicators.calculate(
            candles=candles,
            short_period=short_period,
            long_period=long_period,
            momentum_period=momentum_period,
        )

        short_sma = indicators["short_sma"]
        long_sma = indicators["long_sma"]
        momentum = indicators["momentum"]
        price = indicators["latest_price"]

        bullish_score = 0
        bearish_score = 0

        if short_sma > long_sma:
            bullish_score += 1

        elif short_sma < long_sma:
            bearish_score += 1

        if price > short_sma:
            bullish_score += 1

        elif price < short_sma:
            bearish_score += 1

        if momentum is not None:

            if momentum > 0:
                bullish_score += 1

            elif momentum < 0:
                bearish_score += 1

        if bullish_score > bearish_score:

            trend = "BULLISH"

            confidence = (
                bullish_score / 3.0
            )

        elif bearish_score > bullish_score:

            trend = "BEARISH"

            confidence = (
                bearish_score / 3.0
            )

        else:

            trend = "NEUTRAL"
            confidence = 0.0

        return {
            "status": "COMPLETED",
            "trend": trend,
            "confidence": round(
                confidence,
                4
            ),
            "price": price,
            "short_sma": short_sma,
            "long_sma": long_sma,
            "momentum": momentum,
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
        }
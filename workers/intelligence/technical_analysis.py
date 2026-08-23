from statistics import mean
from typing import List, Dict


class TechnicalAnalyzer:

    @staticmethod
    def closes(candles: List[Dict]) -> List[float]:
        return [float(c["close"]) for c in candles]

    @staticmethod
    def sma(values: List[float], period: int) -> float:
        if not values:
            return 0.0

        window = values[-period:]

        return mean(window)

    @staticmethod
    def ema(values: List[float], period: int) -> float:
        if not values:
            return 0.0

        if len(values) < period:
            return mean(values)

        multiplier = 2 / (period + 1)

        ema_value = mean(values[:period])

        for price in values[period:]:
            ema_value = (
                (price - ema_value) * multiplier
            ) + ema_value

        return ema_value

    @staticmethod
    def rsi(values: List[float], period: int = 14) -> float:

        if len(values) <= period:
            return 50.0

        gains = []
        losses = []

        for index in range(1, len(values)):
            change = values[index] - values[index - 1]

            if change >= 0:
                gains.append(change)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(change))

        recent_gains = gains[-period:]
        recent_losses = losses[-period:]

        average_gain = mean(recent_gains)
        average_loss = mean(recent_losses)

        if average_loss == 0:
            return 100.0 if average_gain > 0 else 50.0

        relative_strength = average_gain / average_loss

        return 100 - (100 / (1 + relative_strength))

    @staticmethod
    def atr(candles: List[Dict], period: int = 14) -> float:

        if len(candles) < 2:
            return 0.0

        true_ranges = []

        for index in range(1, len(candles)):

            current = candles[index]
            previous = candles[index - 1]

            high = float(current["high"])
            low = float(current["low"])
            previous_close = float(previous["close"])

            true_range = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )

            true_ranges.append(true_range)

        return mean(true_ranges[-period:])

    @staticmethod
    def momentum(values: List[float], period: int = 5) -> float:

        if len(values) <= period:
            return 0.0

        previous = values[-period - 1]
        current = values[-1]

        if previous == 0:
            return 0.0

        return ((current - previous) / previous) * 100

    @staticmethod
    def volatility(candles: List[Dict], period: int = 10) -> float:

        if len(candles) < 2:
            return 0.0

        closes = TechnicalAnalyzer.closes(candles)

        returns = []

        for index in range(1, len(closes)):
            previous = closes[index - 1]
            current = closes[index]

            if previous == 0:
                continue

            returns.append(
                ((current - previous) / previous) * 100
            )

        recent = returns[-period:]

        if not recent:
            return 0.0

        average = mean(recent)

        variance = mean(
            [(value - average) ** 2 for value in recent]
        )

        return variance ** 0.5

    def analyze(self, candles: List[Dict]) -> Dict:

        if len(candles) < 3:
            raise ValueError(
                "Technical analysis requires at least 3 candles"
            )

        closes = self.closes(candles)

        sma_fast = self.sma(
            closes,
            5,
        )

        sma_slow = self.sma(
            closes,
            10,
        )

        ema_fast = self.ema(
            closes,
            5,
        )

        ema_slow = self.ema(
            closes,
            10,
        )

        rsi = self.rsi(
            closes,
            14,
        )

        atr = self.atr(
            candles,
            14,
        )

        momentum = self.momentum(
            closes,
            5,
        )

        volatility = self.volatility(
            candles,
            10,
        )

        trend_score = 0.0

        if sma_fast > sma_slow:
            trend_score += 0.25
        elif sma_fast < sma_slow:
            trend_score -= 0.25

        if ema_fast > ema_slow:
            trend_score += 0.25
        elif ema_fast < ema_slow:
            trend_score -= 0.25

        if rsi > 55:
            trend_score += 0.25
        elif rsi < 45:
            trend_score -= 0.25

        if momentum > 0:
            trend_score += 0.25
        elif momentum < 0:
            trend_score -= 0.25

        trend_score = max(
            -1.0,
            min(1.0, trend_score),
        )

        if trend_score > 0.25:
            direction = "BULLISH"
        elif trend_score < -0.25:
            direction = "BEARISH"
        else:
            direction = "NEUTRAL"

        return {
            "price": closes[-1],
            "sma_fast": sma_fast,
            "sma_slow": sma_slow,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "rsi": rsi,
            "atr": atr,
            "momentum": momentum,
            "volatility": volatility,
            "trend_score": trend_score,
            "direction": direction,
        }

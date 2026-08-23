from typing import Dict


class MarketRegimeAnalyzer:

    def analyze(self, technical: Dict) -> Dict:

        trend_score = float(
            technical["trend_score"]
        )

        volatility = float(
            technical["volatility"]
        )

        momentum = float(
            technical["momentum"]
        )

        if abs(trend_score) < 0.25:

            regime = "RANGING"

        elif trend_score >= 0.5:

            regime = "BULL_TREND"

        elif trend_score <= -0.5:

            regime = "BEAR_TREND"

        elif trend_score > 0:

            regime = "WEAK_BULL"

        else:

            regime = "WEAK_BEAR"

        if volatility >= 2.0:
            volatility_state = "HIGH"
        elif volatility >= 0.75:
            volatility_state = "MEDIUM"
        else:
            volatility_state = "LOW"

        if momentum > 0:
            momentum_state = "POSITIVE"
        elif momentum < 0:
            momentum_state = "NEGATIVE"
        else:
            momentum_state = "FLAT"

        return {
            "regime": regime,
            "volatility_state": volatility_state,
            "momentum_state": momentum_state,
            "trend_score": trend_score,
        }

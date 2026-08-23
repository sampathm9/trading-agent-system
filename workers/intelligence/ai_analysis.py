from typing import Dict

from config.intelligence_config import (
    TECHNICAL_WEIGHT,
    REGIME_WEIGHT,
    SENTIMENT_WEIGHT,
    BULLISH_THRESHOLD,
    BEARISH_THRESHOLD,
    MIN_CONFIDENCE,
)


class AIAnalyzer:

    def analyze(
        self,
        technical: Dict,
        regime: Dict,
        sentiment: Dict,
    ) -> Dict:

        technical_score = float(
            technical["trend_score"]
        )

        regime_score = float(
            regime["trend_score"]
        )

        sentiment_score = float(
            sentiment["score"]
        )

        combined_score = (
            technical_score * TECHNICAL_WEIGHT
            + regime_score * REGIME_WEIGHT
            + sentiment_score * SENTIMENT_WEIGHT
        )

        combined_score = max(
            -1.0,
            min(1.0, combined_score),
        )

        if combined_score >= BULLISH_THRESHOLD:

            signal = "BUY"

        elif combined_score <= BEARISH_THRESHOLD:

            signal = "SELL"

        else:

            signal = "HOLD"

        agreement = (
            abs(technical_score)
            + abs(regime_score)
            + abs(sentiment_score)
        ) / 3

        confidence = min(
            1.0,
            0.5 + (agreement * 0.5),
        )

        if confidence < MIN_CONFIDENCE:
            signal = "HOLD"

        explanation = self._build_explanation(
            technical,
            regime,
            sentiment,
            signal,
        )

        return {
            "signal": signal,
            "score": combined_score,
            "confidence": confidence,
            "technical_score": technical_score,
            "regime_score": regime_score,
            "sentiment_score": sentiment_score,
            "explanation": explanation,
        }

    @staticmethod
    def _build_explanation(
        technical: Dict,
        regime: Dict,
        sentiment: Dict,
        signal: str,
    ) -> str:

        return (
            f"Signal={signal}; "
            f"technical={technical['direction']}; "
            f"regime={regime['regime']}; "
            f"sentiment={sentiment['label']}; "
            f"RSI={technical['rsi']:.2f}; "
            f"momentum={technical['momentum']:.2f}%."
        )

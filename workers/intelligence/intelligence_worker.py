from typing import Dict, Iterable, List

from workers.intelligence.technical_analysis import (
    TechnicalAnalyzer,
)

from workers.intelligence.market_regime import (
    MarketRegimeAnalyzer,
)

from workers.intelligence.sentiment import (
    SentimentAnalyzer,
)

from workers.intelligence.ai_analysis import (
    AIAnalyzer,
)


class IntelligenceWorker:

    def __init__(self):

        self.technical = TechnicalAnalyzer()
        self.regime = MarketRegimeAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.ai = AIAnalyzer()

    def analyze(
        self,
        candles: List[Dict],
        news: Iterable[Dict | str] | None = None,
    ) -> Dict:

        technical_result = (
            self.technical.analyze(candles)
        )

        regime_result = (
            self.regime.analyze(
                technical_result
            )
        )

        sentiment_result = (
            self.sentiment.analyze(news)
        )

        ai_result = (
            self.ai.analyze(
                technical_result,
                regime_result,
                sentiment_result,
            )
        )

        return {
            "technical": technical_result,
            "regime": regime_result,
            "sentiment": sentiment_result,
            "ai": ai_result,
        }

    def strategy_signal(
        self,
        candles: List[Dict],
        news: Iterable[Dict | str] | None = None,
    ) -> Dict:

        result = self.analyze(
            candles,
            news,
        )

        ai = result["ai"]

        return {
            "signal": ai["signal"],
            "confidence": ai["confidence"],
            "score": ai["score"],
            "reason": ai["explanation"],
        }

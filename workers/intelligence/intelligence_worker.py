from typing import Dict, Iterable, List, Optional

from config.phase13_config import (
    MAX_QUANTITY,
    MIN_AI_CONFIDENCE,
)

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

from workers.risk.risk_worker import (
    RiskWorker,
)

from workers.strategy.strategy_worker import (
    StrategyWorker,
)


class IntelligenceWorker:

    def __init__(
        self,
        min_ai_confidence: Optional[float] = None,
    ):

        if min_ai_confidence is not None:

            min_ai_confidence = float(
                min_ai_confidence
            )

            if not 0.0 <= min_ai_confidence <= 1.0:
                raise ValueError(
                    "min_ai_confidence must be between 0 and 1."
                )

        self.min_ai_confidence = (
            min_ai_confidence
        )

        self.technical = TechnicalAnalyzer()
        self.regime = MarketRegimeAnalyzer()
        self.sentiment = SentimentAnalyzer()
        self.ai = AIAnalyzer()

        self.strategy = StrategyWorker()
        self.risk = RiskWorker()

    # =========================================================
    # PHASE 12 INTELLIGENCE
    # =========================================================

    def analyze(
        self,
        candles: List[Dict],
        news: Iterable[Dict | str] | None = None,
    ) -> Dict:

        technical_result = (
            self.technical.analyze(
                candles
            )
        )

        regime_result = (
            self.regime.analyze(
                technical_result
            )
        )

        sentiment_result = (
            self.sentiment.analyze(
                news
            )
        )

        ai_result = (
            self.ai.analyze(
                technical_result,
                regime_result,
                sentiment_result,
            )
        )

        # -----------------------------------------------------
        # AI CONFIDENCE FILTER
        # -----------------------------------------------------

        if self.min_ai_confidence is not None:

            confidence = float(
                ai_result.get(
                    "confidence",
                    0.0,
                )
            )

            if confidence < self.min_ai_confidence:

                ai_result = dict(
                    ai_result
                )

                ai_result["signal"] = "NO_TRADE"

                ai_result["explanation"] = (
                    f"{ai_result.get('explanation', '')} "
                    f"AI confidence {confidence:.4f} "
                    f"is below minimum required "
                    f"{self.min_ai_confidence:.4f}."
                ).strip()

        return {
            "technical": technical_result,
            "regime": regime_result,
            "sentiment": sentiment_result,
            "ai": ai_result,
        }

    # =========================================================
    # PHASE 13 COMPATIBILITY
    # =========================================================

    def analyze_market(
        self,
        candles: List[Dict],
        news: Iterable[Dict | str] | None = None,
    ) -> Dict:

        return self.analyze(
            candles,
            news,
        )

    # =========================================================
    # STRATEGY SIGNAL
    # =========================================================

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

    # =========================================================
    # PHASE 13 / 15 / 16 COMPATIBILITY
    # =========================================================

    def create_strategy_signal(
        self,
        intelligence_result: Dict,
    ) -> Dict:

        ai = intelligence_result["ai"]

        signal = str(
            ai["signal"]
        ).upper()

        confidence = float(
            ai["confidence"]
        )

        # -----------------------------------------------------
        # Confidence gate
        # -----------------------------------------------------

        minimum_confidence = (
            self.min_ai_confidence
            if self.min_ai_confidence is not None
            else MIN_AI_CONFIDENCE
        )

        if confidence < minimum_confidence:

            action = "HOLD"

        else:

            signal_to_trend = {
                "BUY": "BULLISH",
                "SELL": "BEARISH",
                "HOLD": "SIDEWAYS",
                "NO_TRADE": "NO_TRADE",
            }

            trend = signal_to_trend.get(
                signal,
                "NO_TRADE",
            )

            action = self.strategy.decide(
                trend
            )

        return {
            "signal": signal,
            "action": action,
            "confidence": confidence,
            "score": float(
                ai["score"]
            ),
            "reason": ai["explanation"],
        }

    # =========================================================
    # RISK
    # =========================================================

    def validate_risk(
        self,
        strategy_result: Dict,
        quantity: int,
    ) -> Dict:

        action = strategy_result["action"]

        approved = self.risk.validate(
            action,
            quantity,
            max_quantity=MAX_QUANTITY,
        )

        return {
            "approved": bool(
                approved
            ),
            "action": action,
            "quantity": quantity,
            "reason": (
                "Trade approved"
                if approved
                else "Trade rejected by risk controls"
            ),
        }

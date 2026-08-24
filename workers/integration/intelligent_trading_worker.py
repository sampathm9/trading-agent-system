from typing import Dict, Iterable, List, Optional

from config.phase13_config import (
    MAX_QUANTITY,
    MIN_AI_CONFIDENCE,
)

from workers.intelligence import IntelligenceWorker
from workers.strategy.strategy_worker import StrategyWorker
from workers.risk.risk_worker import RiskWorker
from workers.execution.execution_worker import ExecutionWorker

from workers.broker.models import (
    OrderRequest,
    OrderResult,
    OrderSide,
)


class IntelligentTradingWorker:

    def __init__(
        self,
        intelligence_worker=None,
        strategy_worker=None,
        risk_worker=None,
        execution_worker=None,
        min_ai_confidence=None,
    ):

        self.intelligence = (
            intelligence_worker
            or IntelligenceWorker()
        )

        self.strategy = (
            strategy_worker
            or StrategyWorker()
        )

        self.risk = (
            risk_worker
            or RiskWorker()
        )

        self.execution = execution_worker

        if self.execution is None:
            raise ValueError(
                "Phase 13 requires an ExecutionWorker "
                "connected to a broker."
            )

        if min_ai_confidence is None:
            min_ai_confidence = MIN_AI_CONFIDENCE

        self.min_ai_confidence = float(
            min_ai_confidence
        )

        self.last_intelligence = None
        self.last_strategy = None
        self.last_risk = None
        self.last_execution = None

    # ---------------------------------------------------------
    # INTELLIGENCE
    # ---------------------------------------------------------

    def analyze_market(
        self,
        candles: List[Dict],
        news: Optional[Iterable[Dict | str]] = None,
    ) -> Dict:

        result = self.intelligence.analyze(
            candles,
            news,
        )

        self.last_intelligence = result

        return result

    # ---------------------------------------------------------
    # STRATEGY
    # ---------------------------------------------------------

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

        if confidence < self.min_ai_confidence:

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

        result = {
            "signal": signal,
            "action": action,
            "confidence": confidence,
            "score": float(
                ai["score"]
            ),
            "reason": ai["explanation"],
        }

        self.last_strategy = result

        return result

    # ---------------------------------------------------------
    # RISK
    # ---------------------------------------------------------

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

        result = {
            "approved": bool(approved),
            "action": action,
            "quantity": quantity,
            "reason": (
                "Trade approved"
                if approved
                else "Trade rejected by risk controls"
            ),
        }

        self.last_risk = result

        return result

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    def execute_signal(
        self,
        symbol: str,
        quantity: int,
        price: float,
        strategy_result: Dict,
    ) -> Optional[OrderResult]:

        action = strategy_result["action"]

        if action not in {"BUY", "SELL"}:

            self.last_execution = {
                "status": "NO_ORDER",
                "reason": (
                    "Strategy action is not executable"
                ),
            }

            return None

        side = (
            OrderSide.BUY
            if action == "BUY"
            else OrderSide.SELL
        )

        order = OrderRequest(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=float(price),
            order_type="MARKET",
            tag="PHASE13_INTELLIGENCE",
        )

        result = self.execution.execute(
            order
        )

        self.last_execution = result

        return result

    # ---------------------------------------------------------
    # COMPLETE DECISION CYCLE
    # ---------------------------------------------------------

    def run_cycle(
        self,
        candles: List[Dict],
        symbol: str,
        quantity: int,
        price: float,
        news: Optional[Iterable[Dict | str]] = None,
    ):

        intelligence = self.analyze_market(
            candles,
            news,
        )

        strategy = self.create_strategy_signal(
            intelligence
        )

        risk = self.validate_risk(
            strategy,
            quantity,
        )

        execution = None

        if risk["approved"]:

            execution = self.execute_signal(
                symbol=symbol,
                quantity=quantity,
                price=price,
                strategy_result=strategy,
            )

        return {
            "intelligence": intelligence,
            "strategy": strategy,
            "risk": risk,
            "execution": execution,
        }

    # ---------------------------------------------------------
    # EOD
    # ---------------------------------------------------------

    def close_all(
        self,
        prices: Dict[str, float],
    ):

        return self.execution.close_all(
            prices
        )

    # ---------------------------------------------------------
    # POSITION
    # ---------------------------------------------------------

    def positions(self):

        return self.execution.positions()

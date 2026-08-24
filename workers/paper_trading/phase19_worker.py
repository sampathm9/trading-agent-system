import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from config.phase19_config import (
    DEFAULT_QUANTITY,
    DEFAULT_SYMBOL,
    INITIAL_CAPITAL,
    MAX_CONSECUTIVE_LOSSES,
    MAX_DAILY_LOSS,
    MAX_TRADES,
    MIN_AI_CONFIDENCE,
    PAPER_ONLY,
    REPORT_DIRECTORY,
    REPORT_FILENAME,
)

from workers.paper_trading.performance_tracker import (
    Phase19PerformanceTracker,
)

from workers.paper_trading.safety_gate import (
    Phase19SafetyGate,
)

from workers.paper_trading.paper_session import (
    Phase19PaperSession,
)


class Phase19PaperTradingWorker:

    def __init__(
        self,
        intelligence_worker_factory,
        broker,
        initial_capital: float = INITIAL_CAPITAL,
    ):

        self.intelligence_worker_factory = (
            intelligence_worker_factory
        )

        self.broker = broker

        self.initial_capital = float(
            initial_capital
        )

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------

    def run(
        self,
        candles: List[Dict],
        symbol: str = DEFAULT_SYMBOL,
        quantity: int = DEFAULT_QUANTITY,
        news: Optional[
            Iterable[Dict | str]
        ] = None,
        min_ai_confidence: float = (
            MIN_AI_CONFIDENCE
        ),
    ) -> Dict:

        if not candles:

            raise ValueError(
                "Phase 19 requires historical "
                "or forward-validation candles."
            )

        if quantity <= 0:

            raise ValueError(
                "Quantity must be positive."
            )

        # -----------------------------------------------------
        # HARD PAPER SAFETY
        # -----------------------------------------------------

        safety_gate = Phase19SafetyGate(
            max_trades=MAX_TRADES,
            max_daily_loss=MAX_DAILY_LOSS,
            max_consecutive_losses=(
                MAX_CONSECUTIVE_LOSSES
            ),
            paper_only=PAPER_ONLY,
            allow_real_broker=False,
        )

        broker_check = (
            safety_gate.validate_broker(
                self.broker
            )
        )

        if not broker_check["allowed"]:

            raise RuntimeError(
                broker_check["reason"]
            )

        intelligence_worker = (
            self.intelligence_worker_factory(
                min_ai_confidence=(
                    min_ai_confidence
                )
            )
        )

        performance = (
            Phase19PerformanceTracker(
                initial_capital=(
                    self.initial_capital
                )
            )
        )

        session = Phase19PaperSession(
            broker=self.broker,
            intelligence_worker=(
                intelligence_worker
            ),
            safety_gate=safety_gate,
            performance_tracker=performance,
            symbol=symbol,
            quantity=quantity,
            min_ai_confidence=(
                min_ai_confidence
            ),
        )

        events = []

        for candle in candles:

            event = session.process_candle(
                candle=candle,
                news=news,
            )

            if event is not None:

                events.append(event)

        final_price = float(
            candles[-1]["close"]
        )

        exit_events = (
            session.close_session(
                final_price=final_price
            )
        )

        metrics = performance.metrics()

        remaining_positions = (
            self.broker.get_positions()
        )

        report = {
            "phase": 19,
            "name": (
                "Paper Trading / "
                "Forward Validation"
            ),
            "symbol": symbol,
            "candles": len(candles),
            "quantity": quantity,
            "min_ai_confidence": (
                min_ai_confidence
            ),
            "paper_only": PAPER_ONLY,
            "broker": (
                type(self.broker).__name__
            ),
            "safety": {
                "broker_check": broker_check,
                "real_broker_allowed": False,
                "real_orders_allowed": False,
                "paper_only": True,
            },
            "events": events,
            "exit_events": exit_events,
            "metrics": metrics,
            "signals": session.signals,
            "trades": performance.trades,
            "remaining_positions": (
                remaining_positions
            ),
        }

        return report

    # ---------------------------------------------------------
    # SAVE REPORT
    # ---------------------------------------------------------

    def save_report(
        self,
        result: Dict,
        filename: str = REPORT_FILENAME,
    ) -> str:

        directory = Path(
            REPORT_DIRECTORY
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = directory / filename

        path.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(path)

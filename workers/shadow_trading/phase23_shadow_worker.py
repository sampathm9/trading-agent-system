import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from config.phase23_config import (
    DEFAULT_MIN_AI_CONFIDENCE,
    DEFAULT_QUANTITY,
    DEFAULT_SYMBOL,
    INITIAL_CAPITAL,
    REPORT_DIRECTORY,
    REPORT_FILENAME,
)

from workers.shadow_trading.market_observer import (
    Phase23MarketObserver,
)

from workers.shadow_trading.shadow_audit_logger import (
    ShadowAuditLogger,
)

from workers.shadow_trading.shadow_observer import (
    Phase23ShadowObserver,
)

from workers.shadow_trading.shadow_safety import (
    Phase23ShadowSafety,
)


class Phase23ShadowTradingWorker:

    def __init__(
        self,
        intelligence_worker_factory,
        initial_capital: float = INITIAL_CAPITAL,
    ):

        self.intelligence_worker_factory = (
            intelligence_worker_factory
        )

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
        min_ai_confidence: float = (
            DEFAULT_MIN_AI_CONFIDENCE
        ),
        news: Optional[
            Iterable[Dict | str]
        ] = None,
    ) -> Dict:

        if not candles:

            raise ValueError(
                "Phase 23 requires market candles."
            )

        safety = Phase23ShadowSafety()

        safety_result = safety.validate()

        if not safety_result["allowed"]:

            raise RuntimeError(
                "Phase 23 shadow safety validation failed."
            )

        intelligence = (
            self.intelligence_worker_factory(
                min_ai_confidence=min_ai_confidence
            )
        )

        observer = Phase23MarketObserver()

        session = Phase23ShadowObserver(
            intelligence_worker=intelligence,
            symbol=symbol,
            quantity=quantity,
            min_ai_confidence=min_ai_confidence,
            initial_capital=self.initial_capital,
        )

        audit_path = (
            Path(REPORT_DIRECTORY)
            / "phase23_shadow_audit.log"
        )

        audit = ShadowAuditLogger(
            str(audit_path)
        )

        audit.log(
            "PHASE23_STARTED",
            {
                "symbol": symbol,
                "quantity": quantity,
                "shadow_mode": True,
                "real_orders_allowed": False,
            },
        )

        observations = []

        for candle in candles:

            observer.observe(candle)

            result = session.process_candle(
                candle=candle,
                news=news,
            )

            observations.append(result)

            audit.log(
                "CANDLE_OBSERVED",
                result,
            )

        final_price = float(
            candles[-1]["close"]
        )

        close_result = session.close_session(
            final_price=final_price,
            timestamp=candles[-1].get(
                "timestamp"
            ),
        )

        if close_result:

            audit.log(
                "SHADOW_POSITION_CLOSED",
                close_result,
            )

        summary = session.summary()

        readiness = self.evaluate_readiness(
            summary
        )

        result = {
            "phase": 23,
            "name": (
                "Shadow Trading / "
                "Live Market Observation"
            ),
            "symbol": symbol,
            "candles": len(candles),
            "observations": observations,
            "market": observer.snapshot(),
            "summary": summary,
            "readiness": readiness,
            "safety": safety_result,
            "real_orders_placed": 0,
            "real_broker_used": False,
        }

        audit.log(
            "PHASE23_COMPLETED",
            {
                "summary": summary,
                "readiness": readiness,
                "real_orders_placed": 0,
            },
        )

        return result

    # ---------------------------------------------------------
    # READINESS
    # ---------------------------------------------------------

    def evaluate_readiness(
        self,
        summary: Dict,
    ) -> Dict:

        checks = {
            "shadow_mode": (
                summary["safety"]["shadow_only"]
            ),
            "real_orders_disabled": (
                summary["safety"][
                    "real_orders_allowed"
                ]
                is False
            ),
            "real_broker_unused": (
                summary["safety"][
                    "real_broker_used"
                ]
                is False
            ),
            "candles_observed": (
                summary["candles_observed"] > 0
            ),
        }

        score = (
            sum(
                1
                for value in checks.values()
                if value
            )
            / len(checks)
        )

        ready = all(checks.values())

        return {
            "ready": ready,
            "score": round(score, 6),
            "classification": (
                "SHADOW_OBSERVATION_READY"
                if ready
                else "SHADOW_OBSERVATION_NOT_READY"
            ),
            "checks": checks,
        }

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

        path = (
            directory
            / filename
        )

        path.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(path)

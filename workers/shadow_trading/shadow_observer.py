from typing import Dict, Iterable, List, Optional

from config.phase23_config import (
    DEFAULT_MIN_AI_CONFIDENCE,
    DEFAULT_QUANTITY,
    MAX_CONSECUTIVE_LOSSES,
    MAX_DAILY_VIRTUAL_LOSS,
    MAX_VIRTUAL_TRADES,
    MIN_SIGNAL_CANDLES,
)

from workers.shadow_trading.shadow_portfolio import (
    ShadowPortfolio,
)


class Phase23ShadowObserver:

    def __init__(
        self,
        intelligence_worker,
        symbol: str,
        quantity: int = DEFAULT_QUANTITY,
        min_ai_confidence: float = DEFAULT_MIN_AI_CONFIDENCE,
        initial_capital: float = 100000.0,
    ):

        self.intelligence = intelligence_worker
        self.symbol = symbol
        self.quantity = int(quantity)
        self.min_ai_confidence = float(
            min_ai_confidence
        )

        self.portfolio = ShadowPortfolio(
            initial_capital=initial_capital
        )

        self.history: List[Dict] = []
        self.observations: List[Dict] = []
        self.signals: List[Dict] = []
        self.rejected_signals: List[Dict] = []

    # ---------------------------------------------------------
    # SAFETY
    # ---------------------------------------------------------

    def safety_status(self) -> Dict:

        return {
            "shadow_only": True,
            "real_orders_allowed": False,
            "real_broker_used": False,
        }

    # ---------------------------------------------------------
    # SIGNAL
    # ---------------------------------------------------------

    def get_signal(
        self,
        news: Optional[Iterable[Dict | str]] = None,
    ) -> Dict:

        if len(self.history) < MIN_SIGNAL_CANDLES:

            return {
                "signal": "HOLD",
                "confidence": 0.0,
                "score": 0.0,
                "reason": (
                    "Insufficient candles "
                    "for signal generation."
                ),
            }

        return self.intelligence.strategy_signal(
            candles=self.history,
            news=news,
        )

    # ---------------------------------------------------------
    # RISK
    # ---------------------------------------------------------

    def risk_allowed(self) -> Dict:

        snapshot = self.portfolio.snapshot()

        if (
            len(self.portfolio.trades)
            >= MAX_VIRTUAL_TRADES
        ):
            return {
                "allowed": False,
                "reason": "MAX_VIRTUAL_TRADES_REACHED",
            }

        if (
            self.portfolio.consecutive_losses
            >= MAX_CONSECUTIVE_LOSSES
        ):
            return {
                "allowed": False,
                "reason": "MAX_CONSECUTIVE_LOSSES_REACHED",
            }

        if (
            snapshot["realized_pnl"]
            <= -MAX_DAILY_VIRTUAL_LOSS
        ):
            return {
                "allowed": False,
                "reason": "MAX_DAILY_VIRTUAL_LOSS_REACHED",
            }

        return {
            "allowed": True,
            "reason": "OK",
        }

    # ---------------------------------------------------------
    # PROCESS
    # ---------------------------------------------------------

    def process_candle(
        self,
        candle: Dict,
        news: Optional[Iterable[Dict | str]] = None,
    ) -> Dict:

        self.history.append(candle)

        price = float(candle["close"])

        self.portfolio.mark_to_market(
            price
        )

        if len(self.history) < MIN_SIGNAL_CANDLES:

            result = {
                "action": "OBSERVE",
                "price": price,
                "reason": "INSUFFICIENT_HISTORY",
            }

            self.observations.append(result)

            return result

        risk = self.risk_allowed()

        if not risk["allowed"]:

            result = {
                "action": "BLOCKED",
                "price": price,
                "reason": risk["reason"],
            }

            self.rejected_signals.append(result)
            self.observations.append(result)

            return result

        signal = self.get_signal(news)

        signal_name = str(
            signal.get(
                "signal",
                "HOLD",
            )
        ).upper()

        confidence = float(
            signal.get(
                "confidence",
                0.0,
            )
        )

        position_open = (
            self.portfolio.position_quantity > 0
        )

        record = {
            "price": price,
            "signal": signal_name,
            "confidence": confidence,
            "score": signal.get(
                "score",
                0.0,
            ),
            "reason": signal.get(
                "reason",
                "",
            ),
            "position_open": position_open,
        }

        self.signals.append(record)

        # -----------------------------------------------------
        # VIRTUAL BUY
        # -----------------------------------------------------

        if (
            signal_name == "BUY"
            and confidence >= self.min_ai_confidence
            and not position_open
        ):

            trade = self.portfolio.enter(
                symbol=self.symbol,
                quantity=self.quantity,
                price=price,
                timestamp=candle.get("timestamp"),
                reason="PHASE23_SHADOW_ENTRY",
            )

            result = {
                **record,
                "action": "SHADOW_BUY",
                "virtual_order": trade,
            }

            self.observations.append(result)

            return result

        # -----------------------------------------------------
        # VIRTUAL SELL
        # -----------------------------------------------------

        if (
            signal_name == "SELL"
            and confidence >= self.min_ai_confidence
            and position_open
        ):

            trade = self.portfolio.exit(
                price=price,
                timestamp=candle.get("timestamp"),
                reason="PHASE23_SHADOW_EXIT",
            )

            result = {
                **record,
                "action": "SHADOW_SELL",
                "virtual_order": trade,
            }

            self.observations.append(result)

            return result

        result = {
            **record,
            "action": "HOLD",
        }

        self.observations.append(result)

        return result

    # ---------------------------------------------------------
    # SESSION CLOSE
    # ---------------------------------------------------------

    def close_session(
        self,
        final_price: float,
        timestamp=None,
    ):

        trade = self.portfolio.close(
            final_price=final_price,
            timestamp=timestamp,
        )

        if trade is None:
            return None

        result = {
            "action": "SHADOW_SESSION_CLOSE",
            "virtual_order": trade,
        }

        self.observations.append(result)

        return result

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    def summary(self) -> Dict:

        snapshot = self.portfolio.snapshot()

        total_signals = len(self.signals)

        buy_signals = sum(
            1
            for item in self.signals
            if item["signal"] == "BUY"
        )

        sell_signals = sum(
            1
            for item in self.signals
            if item["signal"] == "SELL"
        )

        return {
            "symbol": self.symbol,
            "candles_observed": len(self.history),
            "observations": len(
                self.observations
            ),
            "signals": total_signals,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "rejected_signals": len(
                self.rejected_signals
            ),
            **snapshot,
            "safety": self.safety_status(),
        }

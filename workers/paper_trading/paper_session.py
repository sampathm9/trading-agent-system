from typing import Dict, Iterable, List, Optional

from workers.broker.models import (
    OrderRequest,
    OrderSide,
)


class Phase19PaperSession:

    def __init__(
        self,
        broker,
        intelligence_worker,
        safety_gate,
        performance_tracker,
        symbol: str,
        quantity: int,
        min_ai_confidence: float,
    ):

        self.broker = broker

        self.intelligence = (
            intelligence_worker
        )

        self.safety_gate = safety_gate

        self.performance = (
            performance_tracker
        )

        self.symbol = symbol

        self.quantity = int(quantity)

        self.min_ai_confidence = float(
            min_ai_confidence
        )

        self.history: List[Dict] = []

        self.signals: List[Dict] = []

        self.rejected_signals: List[Dict] = []

    # ---------------------------------------------------------
    # SIGNAL
    # ---------------------------------------------------------

    def get_signal(
        self,
        news: Optional[
            Iterable[Dict | str]
        ],
    ) -> Dict:

        return self.intelligence.strategy_signal(
            candles=self.history,
            news=news,
        )

    # ---------------------------------------------------------
    # PROCESS CANDLE
    # ---------------------------------------------------------

    def process_candle(
        self,
        candle: Dict,
        news: Optional[
            Iterable[Dict | str]
        ] = None,
    ) -> Optional[Dict]:

        # -----------------------------------------------------
        # Always add the new candle to history first.
        # -----------------------------------------------------

        self.history.append(candle)

        price = float(
            candle["close"]
        )

        # -----------------------------------------------------
        # TechnicalAnalyzer requires at least 3 candles.
        #
        # Candle 1:
        #   Store only.
        #
        # Candle 2:
        #   Store only.
        #
        # Candle 3+:
        #   Intelligence analysis can begin.
        # -----------------------------------------------------

        if len(self.history) < 3:

            return {
                "action": "WARMUP",
                "reason": (
                    "Waiting for at least "
                    "3 candles for technical analysis."
                ),
                "candles_available": len(
                    self.history
                ),
                "candles_required": 3,
                "price": price,
            }

        # -----------------------------------------------------
        # SAFETY GATE
        # -----------------------------------------------------

        safety = self.safety_gate.can_trade(
            total_trades=(
                len(self.performance.trades)
            ),
            realized_pnl=(
                self.performance.realized_pnl
            ),
            consecutive_losses=(
                self.performance.consecutive_losses
            ),
        )

        if not safety["allowed"]:

            return {
                "action": "BLOCKED",
                "reason": safety["reason"],
                "price": price,
            }

        # -----------------------------------------------------
        # INTELLIGENCE
        # -----------------------------------------------------

        signal = self.get_signal(
            news
        )

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

        position = (
            self.broker.get_positions().get(
                self.symbol
            )
        )

        current_quantity = (
            int(position["quantity"])
            if position
            else 0
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
        }

        self.signals.append(
            record
        )

        # -----------------------------------------------------
        # BUY
        # -----------------------------------------------------

        if (
            signal_name == "BUY"
            and confidence
            >= self.min_ai_confidence
            and current_quantity == 0
        ):

            order = OrderRequest(
                symbol=self.symbol,
                side=OrderSide.BUY,
                quantity=self.quantity,
                price=price,
                order_type="MARKET",
                tag="PHASE19_PAPER_ENTRY",
            )

            result = self.broker.place_order(
                order
            )

            # -------------------------------------------------
            # Record rejected orders separately.
            # -------------------------------------------------

            if str(
                result.status
            ).upper() != "FILLED":

                rejected = {
                    **record,
                    "action": "BUY_REJECTED",
                    "order_id": result.order_id,
                    "status": str(
                        result.status
                    ),
                    "message": result.message,
                }

                self.rejected_signals.append(
                    rejected
                )

                return rejected

            return {
                **record,
                "action": "BUY",
                "order_id": result.order_id,
                "status": str(
                    result.status
                ),
            }

        # -----------------------------------------------------
        # SELL
        # -----------------------------------------------------

        if (
            signal_name == "SELL"
            and confidence
            >= self.min_ai_confidence
            and current_quantity > 0
        ):

            order = OrderRequest(
                symbol=self.symbol,
                side=OrderSide.SELL,
                quantity=current_quantity,
                price=price,
                order_type="MARKET",
                tag="PHASE19_PAPER_EXIT",
            )

            result = self.broker.place_order(
                order
            )

            # -------------------------------------------------
            # Only filled SELL orders become completed trades.
            # -------------------------------------------------

            if str(
                result.status
            ).upper() != "FILLED":

                rejected = {
                    **record,
                    "action": "SELL_REJECTED",
                    "order_id": result.order_id,
                    "status": str(
                        result.status
                    ),
                    "message": result.message,
                }

                self.rejected_signals.append(
                    rejected
                )

                return rejected

            self.performance.record_trade(
                result
            )

            return {
                **record,
                "action": "SELL",
                "order_id": result.order_id,
                "status": str(
                    result.status
                ),
                "realized_pnl": (
                    result.realized_pnl
                ),
            }

        # -----------------------------------------------------
        # HOLD
        # -----------------------------------------------------

        return {
            **record,
            "action": "HOLD",
        }

    # ---------------------------------------------------------
    # END OF SESSION
    # ---------------------------------------------------------

    def close_session(
        self,
        final_price: float,
    ) -> List[Dict]:

        positions = (
            self.broker.get_positions()
        )

        if self.symbol not in positions:

            return []

        position = positions[
            self.symbol
        ]

        quantity = int(
            position["quantity"]
        )

        if quantity <= 0:

            return []

        results = (
            self.broker.close_all_positions(
                {
                    self.symbol: float(
                        final_price
                    )
                }
            )
        )

        output = []

        for result in results:

            if str(
                result.status
            ).upper() != "FILLED":

                self.rejected_signals.append(
                    {
                        "action": "EOD_EXIT_REJECTED",
                        "order_id": result.order_id,
                        "symbol": result.symbol,
                        "quantity": result.quantity,
                        "price": result.price,
                        "status": str(
                            result.status
                        ),
                    }
                )

                continue

            self.performance.record_trade(
                result
            )

            output.append(
                {
                    "order_id": (
                        result.order_id
                    ),
                    "symbol": (
                        result.symbol
                    ),
                    "quantity": (
                        result.quantity
                    ),
                    "price": result.price,
                    "realized_pnl": (
                        result.realized_pnl
                    ),
                    "status": str(
                        result.status
                    ),
                }
            )

        return output

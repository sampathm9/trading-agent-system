class BacktestWorker:

    def __init__(self, trend_worker=None, decision_worker=None):
        from workers.intelligence.trend_worker import TrendWorker
        from workers.decision.decision_worker import DecisionWorker

        self.trend_worker = trend_worker or TrendWorker()
        self.decision_worker = decision_worker or DecisionWorker()

    def run(
        self,
        candles,
        symbol="NIFTY",
        quantity=1,
        short_period=5,
        long_period=10,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=None
    ):

        if not candles:
            raise ValueError("No candle data provided")

        if len(candles) <= long_period:
            raise ValueError(
                "Not enough candles for the selected long_period"
            )

        trades = []

        position = None

        total_realized_pnl = 0.0
        peak_pnl = 0.0
        max_drawdown = 0.0

        for i in range(long_period, len(candles)):

            current_price = float(candles[i]["close"])

            # -------------------------------------------------
            # POSITION MANAGEMENT
            # -------------------------------------------------

            if position is not None:

                entry_price = position["entry_price"]

                stop_loss_price = (
                    entry_price * (1 - stop_loss_pct)
                )

                take_profit_price = (
                    entry_price * (1 + take_profit_pct)
                )

                # STOP LOSS
                if current_price <= stop_loss_price:

                    pnl = (
                        current_price - entry_price
                    ) * position["quantity"]

                    total_realized_pnl += pnl

                    trades.append({
                        "type": "STOP_LOSS",
                        "symbol": symbol,
                        "quantity": position["quantity"],
                        "price": current_price,
                        "entry_price": entry_price,
                        "pnl": pnl,
                        "index": i
                    })

                    position = None

                    peak_pnl = max(
                        peak_pnl,
                        total_realized_pnl
                    )

                    drawdown = peak_pnl - total_realized_pnl

                    max_drawdown = max(
                        max_drawdown,
                        drawdown
                    )

                    continue

                # TAKE PROFIT
                if current_price >= take_profit_price:

                    pnl = (
                        current_price - entry_price
                    ) * position["quantity"]

                    total_realized_pnl += pnl

                    trades.append({
                        "type": "TAKE_PROFIT",
                        "symbol": symbol,
                        "quantity": position["quantity"],
                        "price": current_price,
                        "entry_price": entry_price,
                        "pnl": pnl,
                        "index": i
                    })

                    position = None

                    peak_pnl = max(
                        peak_pnl,
                        total_realized_pnl
                    )

                    drawdown = peak_pnl - total_realized_pnl

                    max_drawdown = max(
                        max_drawdown,
                        drawdown
                    )

                    continue

            # -------------------------------------------------
            # DAILY LOSS PROTECTION
            # -------------------------------------------------

            if (
                max_daily_loss is not None
                and total_realized_pnl <= -abs(max_daily_loss)
            ):

                if position is not None:

                    entry_price = position["entry_price"]

                    pnl = (
                        current_price - entry_price
                    ) * position["quantity"]

                    total_realized_pnl += pnl

                    trades.append({
                        "type": "RISK_EXIT",
                        "symbol": symbol,
                        "quantity": position["quantity"],
                        "price": current_price,
                        "entry_price": entry_price,
                        "pnl": pnl,
                        "index": i
                    })

                    position = None

                break

            # -------------------------------------------------
            # SIGNAL GENERATION
            # -------------------------------------------------

            # IMPORTANT:
            # Use candles BEFORE the current candle.
            # This prevents same-candle lookahead.

            historical_candles = candles[:i]

            trend_result = self.trend_worker.analyze(
                historical_candles,
                short_period=short_period,
                long_period=long_period
            )

            trend = trend_result["trend"]

            decision = self.decision_worker.decide(trend)

            action = decision["action"]

            # -------------------------------------------------
            # ENTRY
            # -------------------------------------------------

            if position is None and action == "BUY":

                position = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "entry_price": current_price,
                    "entry_index": i
                }

                trades.append({
                    "type": "BUY",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "index": i
                })

            # -------------------------------------------------
            # SIGNAL EXIT
            # -------------------------------------------------

            elif position is not None and action == "SELL":

                entry_price = position["entry_price"]

                pnl = (
                    current_price - entry_price
                ) * position["quantity"]

                total_realized_pnl += pnl

                trades.append({
                    "type": "SELL",
                    "symbol": symbol,
                    "quantity": position["quantity"],
                    "price": current_price,
                    "entry_price": entry_price,
                    "pnl": pnl,
                    "index": i
                })

                position = None

                peak_pnl = max(
                    peak_pnl,
                    total_realized_pnl
                )

                drawdown = peak_pnl - total_realized_pnl

                max_drawdown = max(
                    max_drawdown,
                    drawdown
                )

        # -----------------------------------------------------
        # FINAL EXIT
        # -----------------------------------------------------

        if position is not None:

            final_price = float(candles[-1]["close"])

            entry_price = position["entry_price"]

            pnl = (
                final_price - entry_price
            ) * position["quantity"]

            total_realized_pnl += pnl

            trades.append({
                "type": "FINAL_EXIT",
                "symbol": symbol,
                "quantity": position["quantity"],
                "price": final_price,
                "entry_price": entry_price,
                "pnl": pnl,
                "index": len(candles) - 1
            })

            position = None

            peak_pnl = max(
                peak_pnl,
                total_realized_pnl
            )

            drawdown = peak_pnl - total_realized_pnl

            max_drawdown = max(
                max_drawdown,
                drawdown
            )

        # -----------------------------------------------------
        # STATISTICS
        # -----------------------------------------------------

        completed_trades = [
            trade
            for trade in trades
            if trade["type"] in (
                "SELL",
                "STOP_LOSS",
                "TAKE_PROFIT",
                "FINAL_EXIT",
                "RISK_EXIT"
            )
        ]

        winning_trades = [
            trade
            for trade in completed_trades
            if trade["pnl"] > 0
        ]

        losing_trades = [
            trade
            for trade in completed_trades
            if trade["pnl"] < 0
        ]

        total_completed = len(completed_trades)

        win_rate = (
            len(winning_trades) / total_completed * 100
            if total_completed > 0
            else 0.0
        )

        average_win = (
            sum(
                trade["pnl"]
                for trade in winning_trades
            ) / len(winning_trades)
            if winning_trades
            else 0.0
        )

        average_loss = (
            sum(
                trade["pnl"]
                for trade in losing_trades
            ) / len(losing_trades)
            if losing_trades
            else 0.0
        )

        return {
            "symbol": symbol,
            "total_candles": len(candles),
            "total_orders": len(trades),
            "completed_trades": total_completed,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "average_win": average_win,
            "average_loss": average_loss,
            "max_drawdown": max_drawdown,
            "total_realized_pnl": total_realized_pnl,
            "trades": trades
        }
from workers.backtest.backtest_worker import BacktestWorker

from workers.costs.trading_cost_worker import (
    TradingCostWorker
)

from workers.historical.phase3_data_validator import (
    Phase3DataValidator
)

from workers.analytics.performance_worker import (
    PerformanceWorker
)


class RealisticBacktestWorker:

    def __init__(
        self,
        decision_worker=None,
        cost_worker=None
    ):
        self.backtest_worker = BacktestWorker(
            decision_worker=decision_worker
        )

        self.cost_worker = (
            cost_worker
            or TradingCostWorker()
        )

        self.validator = Phase3DataValidator()

        self.performance = PerformanceWorker()

    def _get_timestamp(
        self,
        candle,
        index
    ):
        return (
            candle.get("timestamp")
            or candle.get("datetime")
            or candle.get("date")
            or str(index)
        )

    def run(
        self,
        candles,
        symbol,
        quantity=1,
        short_period=5,
        long_period=10,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=None
    ):
        validation = self.validator.validate(
            candles
        )

        result = self.backtest_worker.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            short_period=short_period,
            long_period=long_period,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            max_daily_loss=max_daily_loss
        )

        raw_trades = result.get(
            "trades",
            []
        )

        processed_trades = []

        entry_price = None
        entry_index = None

        for trade in raw_trades:

            trade_copy = dict(trade)

            trade_type = trade.get("type")
            price = trade.get("price")
            index = trade.get("index")

            if trade_type == "BUY":

                entry_price = float(price)

                entry_index = index

                trade_copy["slippage_price"] = (
                    self.cost_worker.apply_slippage(
                        price,
                        "BUY"
                    )
                )

                processed_trades.append(
                    trade_copy
                )

                continue

            if trade_type in (
                "TAKE_PROFIT",
                "STOP_LOSS",
                "FINAL_EXIT"
            ):

                if entry_price is not None:

                    exit_price = float(price)

                    effective_entry = (
                        self.cost_worker.apply_slippage(
                            entry_price,
                            "BUY"
                        )
                    )

                    effective_exit = (
                        self.cost_worker.apply_slippage(
                            exit_price,
                            "SELL"
                        )
                    )

                    cost_result = (
                        self.cost_worker.calculate_trade(
                            effective_entry,
                            effective_exit,
                            quantity
                        )
                    )

                    trade_copy["entry_price_gross"] = (
                        entry_price
                    )

                    trade_copy["exit_price_gross"] = (
                        exit_price
                    )

                    trade_copy["effective_entry_price"] = (
                        effective_entry
                    )

                    trade_copy["effective_exit_price"] = (
                        effective_exit
                    )

                    trade_copy["gross_pnl"] = (
                        cost_result["gross_pnl"]
                    )

                    trade_copy["total_cost"] = (
                        cost_result["total_cost"]
                    )

                    trade_copy["net_pnl"] = (
                        cost_result["net_pnl"]
                    )

                    if (
                        isinstance(index, int)
                        and index < len(candles)
                    ):
                        candle = candles[index]
                    else:
                        candle = {}

                    trade_copy["timestamp"] = (
                        self._get_timestamp(
                            candle,
                            index
                        )
                    )

                    trade_copy["entry_index"] = (
                        entry_index
                    )

                    processed_trades.append(
                        trade_copy
                    )

                    entry_price = None
                    entry_index = None

        completed = [
            trade
            for trade in processed_trades
            if "net_pnl" in trade
        ]

        metrics = self.performance.analyze(
            completed
        )

        daily = self.performance.daily_pnl(
            completed
        )

        monthly = self.performance.monthly_pnl(
            completed
        )

        return {
            "status": "COMPLETED",
            "symbol": symbol,
            "quantity": quantity,
            "total_candles": len(candles),
            "validation": validation,
            "raw_result": result,
            "trades": processed_trades,
            "completed_trades": completed,
            "performance": metrics,
            "daily_pnl": daily,
            "monthly_pnl": monthly
        }
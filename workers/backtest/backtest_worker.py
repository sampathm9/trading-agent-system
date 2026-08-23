class BacktestWorker:

    def __init__(self, trading_cycle_worker=None):
        self.trading_cycle_worker = trading_cycle_worker

    def run(
        self,
        candles,
        symbol,
        quantity=1,
        starting_cash=100000.0
    ):

        results = []
        cash = starting_cash
        position = None
        trades = []

        for index in range(len(candles)):

            current_candle = candles[index]
            price = current_candle["close"]

            historical_candles = candles[:index + 1]

            if self.trading_cycle_worker is None:
                from workers.trading.trading_cycle_worker import TradingCycleWorker
                cycle_worker = TradingCycleWorker()
            else:
                cycle_worker = self.trading_cycle_worker

            result = cycle_worker.run(
                historical_candles,
                symbol,
                quantity,
                price
            )

            execution = result.get("execution", {})
            action = result.get("decision", {}).get("action")

            if execution.get("status") == "EXECUTED":

                if action == "BUY" and position is None:

                    position = {
                        "symbol": symbol,
                        "quantity": quantity,
                        "entry_price": price,
                        "entry_index": index
                    }

                elif action == "SELL" and position is not None:

                    entry_price = position["entry_price"]

                    pnl = (
                        price - entry_price
                    ) * position["quantity"]

                    cash += pnl

                    trades.append({
                        "symbol": symbol,
                        "quantity": position["quantity"],
                        "entry_price": entry_price,
                        "exit_price": price,
                        "pnl": pnl,
                        "entry_index": position["entry_index"],
                        "exit_index": index,
                        "exit_reason": "SIGNAL"
                    })

                    position = None

            results.append({
                "index": index,
                "price": price,
                "action": action,
                "result": result
            })

        # End-of-backtest exit
        if position is not None:

            final_price = candles[-1]["close"]

            entry_price = position["entry_price"]

            pnl = (
                final_price - entry_price
            ) * position["quantity"]

            cash += pnl

            trades.append({
                "symbol": symbol,
                "quantity": position["quantity"],
                "entry_price": entry_price,
                "exit_price": final_price,
                "pnl": pnl,
                "entry_index": position["entry_index"],
                "exit_index": len(candles) - 1,
                "exit_reason": "END_OF_BACKTEST"
            })

            position = None

        total_pnl = sum(
            trade["pnl"]
            for trade in trades
        )

        winning_trades = [
            trade
            for trade in trades
            if trade["pnl"] > 0
        ]

        losing_trades = [
            trade
            for trade in trades
            if trade["pnl"] < 0
        ]

        win_rate = (
            len(winning_trades) / len(trades) * 100
            if trades
            else 0.0
        )

        return {
            "starting_cash": starting_cash,
            "ending_cash": cash,
            "total_pnl": total_pnl,
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "open_position": position,
            "trades": trades,
            "results": results
        }
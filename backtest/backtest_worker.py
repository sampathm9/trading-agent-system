class BacktestWorker:

    def run(self, candles, strategy):

        if not candles:
            return {
                "status": "FAILED",
                "reason": "No candle data"
            }

        trades = []
        wins = 0
        losses = 0
        total_pnl = 0.0

        for i in range(1, len(candles)):

            previous_close = float(candles[i - 1]["close"])
            current_close = float(candles[i]["close"])

            signal = strategy.generate_signal(
                previous_close,
                current_close
            )

            if signal == "BUY":
                pnl = current_close - previous_close

            elif signal == "SELL":
                pnl = previous_close - current_close

            else:
                pnl = 0.0

            if signal in ("BUY", "SELL"):

                trades.append({
                    "index": i,
                    "signal": signal,
                    "entry": previous_close,
                    "exit": current_close,
                    "pnl": pnl
                })

                total_pnl += pnl

                if pnl > 0:
                    wins += 1

                elif pnl < 0:
                    losses += 1

        total_trades = wins + losses

        if total_trades > 0:
            win_rate = (wins / total_trades) * 100
        else:
            win_rate = 0.0

        return {
            "status": "COMPLETED",
            "strategy": strategy.name,
            "trades": trades,
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_pnl": total_pnl
        }
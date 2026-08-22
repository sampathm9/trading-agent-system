class BacktestWorker:

    def run_momentum_backtest(self, candles):

        if len(candles) < 2:
            return {
                "name": "Momentum",
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "score": 0.0,
                "confidence": 0.0
            }

        trades = 0
        wins = 0
        losses = 0
        total_pnl = 0.0

        for i in range(1, len(candles)):

            previous_close = float(
                candles[i - 1]["close"]
            )

            current_close = float(
                candles[i]["close"]
            )

            if current_close > previous_close:

                entry_price = current_close

                if i + 1 < len(candles):

                    exit_price = float(
                        candles[i + 1]["close"]
                    )

                    pnl = exit_price - entry_price

                    trades += 1
                    total_pnl += pnl

                    if pnl > 0:
                        wins += 1
                    else:
                        losses += 1

        if trades > 0:
            win_rate = wins / trades
        else:
            win_rate = 0.0

        score = win_rate

        confidence = min(
            1.0,
            win_rate
        )

        return {
            "name": "Momentum",
            "trades": trades,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 4),
            "total_pnl": round(total_pnl, 2),
            "score": round(score, 4),
            "confidence": round(confidence, 4)
        }
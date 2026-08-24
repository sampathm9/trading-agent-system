from typing import Dict, Iterable, List


class PerformanceAnalyzer:

    def analyze(
        self,
        initial_capital: float,
        trades: Iterable[Dict],
    ) -> Dict:

        trades = list(trades)

        realized_pnl = sum(
            float(trade.get("pnl", 0.0))
            for trade in trades
        )

        winning_trades = [
            trade
            for trade in trades
            if float(trade.get("pnl", 0.0)) > 0
        ]

        losing_trades = [
            trade
            for trade in trades
            if float(trade.get("pnl", 0.0)) < 0
        ]

        total_trades = len(trades)

        win_rate = (
            len(winning_trades) / total_trades
            if total_trades
            else 0.0
        )

        loss_rate = (
            len(losing_trades) / total_trades
            if total_trades
            else 0.0
        )

        equity = float(initial_capital)

        peak_equity = equity
        max_drawdown = 0.0

        equity_curve = []

        for trade in trades:

            equity += float(
                trade.get("pnl", 0.0)
            )

            peak_equity = max(
                peak_equity,
                equity,
            )

            drawdown = peak_equity - equity

            max_drawdown = max(
                max_drawdown,
                drawdown,
            )

            equity_curve.append(
                {
                    "timestamp": trade.get(
                        "timestamp"
                    ),
                    "equity": equity,
                    "drawdown": drawdown,
                }
            )

        return {
            "initial_capital": float(
                initial_capital
            ),
            "final_equity": equity,
            "realized_pnl": realized_pnl,
            "return_percentage": (
                realized_pnl
                / initial_capital
                * 100.0
                if initial_capital
                else 0.0
            ),
            "total_trades": total_trades,
            "winning_trades": len(
                winning_trades
            ),
            "losing_trades": len(
                losing_trades
            ),
            "win_rate": win_rate,
            "loss_rate": loss_rate,
            "max_drawdown": max_drawdown,
            "equity_curve": equity_curve,
        }

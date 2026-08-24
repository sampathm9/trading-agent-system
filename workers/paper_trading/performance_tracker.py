from typing import Dict, List


class Phase19PerformanceTracker:

    def __init__(
        self,
        initial_capital: float,
    ):

        self.initial_capital = float(
            initial_capital
        )

        self.realized_pnl = 0.0

        self.trades: List[Dict] = []

        self.winning_trades = 0
        self.losing_trades = 0

        self.consecutive_losses = 0
        self.max_consecutive_losses = 0

    # ---------------------------------------------------------
    # RECORD TRADE
    # ---------------------------------------------------------

    def record_trade(
        self,
        order_result,
    ) -> None:

        realized_pnl = order_result.realized_pnl

        if realized_pnl is None:

            return

        pnl = float(realized_pnl)

        self.realized_pnl += pnl

        if pnl > 0:

            self.winning_trades += 1

            self.consecutive_losses = 0

        elif pnl < 0:

            self.losing_trades += 1

            self.consecutive_losses += 1

            self.max_consecutive_losses = max(
                self.max_consecutive_losses,
                self.consecutive_losses,
            )

        self.trades.append(
            {
                "order_id": order_result.order_id,
                "symbol": order_result.symbol,
                "side": str(
                    order_result.side
                ),
                "quantity": order_result.quantity,
                "price": order_result.price,
                "realized_pnl": pnl,
                "status": str(
                    order_result.status
                ),
            }
        )

    # ---------------------------------------------------------
    # METRICS
    # ---------------------------------------------------------

    def metrics(self) -> Dict:

        total_trades = (
            self.winning_trades
            + self.losing_trades
        )

        win_rate = (
            self.winning_trades
            / total_trades
            if total_trades
            else 0.0
        )

        return {
            "initial_capital": (
                self.initial_capital
            ),
            "realized_pnl": round(
                self.realized_pnl,
                6,
            ),
            "ending_capital": round(
                self.initial_capital
                + self.realized_pnl,
                6,
            ),
            "total_trades": total_trades,
            "winning_trades": (
                self.winning_trades
            ),
            "losing_trades": (
                self.losing_trades
            ),
            "win_rate": round(
                win_rate,
                6,
            ),
            "max_consecutive_losses": (
                self.max_consecutive_losses
            ),
        }

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    def report(self) -> Dict:

        return {
            "metrics": self.metrics(),
            "trades": list(self.trades),
        }

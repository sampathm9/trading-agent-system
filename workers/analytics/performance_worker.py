from collections import defaultdict


class PerformanceWorker:

    def analyze(
        self,
        trades
    ):

        pnls = [
            float(
                trade.get(
                    "net_pnl",
                    trade.get(
                        "pnl",
                        0.0
                    )
                )
            )
            for trade in trades
        ]

        winning = [
            pnl
            for pnl in pnls
            if pnl > 0
        ]

        losing = [
            pnl
            for pnl in pnls
            if pnl < 0
        ]

        total_trades = len(pnls)

        win_rate = (
            len(winning)
            / total_trades
            * 100
            if total_trades
            else 0.0
        )

        gross_profit = sum(
            winning
        )

        gross_loss = abs(
            sum(losing)
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else None
        )

        total_pnl = sum(
            pnls
        )

        average_trade = (
            total_pnl / total_trades
            if total_trades
            else 0.0
        )

        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0

        for pnl in pnls:

            equity += pnl

            peak = max(
                peak,
                equity
            )

            drawdown = (
                peak - equity
            )

            max_drawdown = max(
                max_drawdown,
                drawdown
            )

        return {
            "total_trades": total_trades,
            "winning_trades": len(
                winning
            ),
            "losing_trades": len(
                losing
            ),
            "win_rate": round(
                win_rate,
                2
            ),
            "gross_profit": round(
                gross_profit,
                4
            ),
            "gross_loss": round(
                gross_loss,
                4
            ),
            "profit_factor": (
                round(
                    profit_factor,
                    4
                )
                if profit_factor is not None
                else None
            ),
            "total_pnl": round(
                total_pnl,
                4
            ),
            "average_trade": round(
                average_trade,
                4
            ),
            "max_drawdown": round(
                max_drawdown,
                4
            ),
            "max_consecutive_wins":
                self._max_consecutive(
                    pnls,
                    positive=True
                ),
            "max_consecutive_losses":
                self._max_consecutive(
                    pnls,
                    positive=False
                )
        }

    def daily_pnl(
        self,
        trades
    ):

        result = defaultdict(float)

        for trade in trades:

            pnl = float(
                trade.get(
                    "net_pnl",
                    trade.get(
                        "pnl",
                        0.0
                    )
                )
            )

            date_key = (
                trade.get(
                    "date"
                )
                or trade.get(
                    "timestamp",
                    "UNKNOWN"
                )
            )

            if isinstance(
                date_key,
                str
            ):

                date_key = (
                    date_key[:10]
                )

            result[date_key] += pnl

        return {
            key: round(
                value,
                4
            )
            for key, value in result.items()
        }

    def monthly_pnl(
        self,
        trades
    ):

        result = defaultdict(float)

        for trade in trades:

            pnl = float(
                trade.get(
                    "net_pnl",
                    trade.get(
                        "pnl",
                        0.0
                    )
                )
            )

            date_key = (
                trade.get(
                    "date"
                )
                or trade.get(
                    "timestamp",
                    "UNKNOWN"
                )
            )

            if isinstance(
                date_key,
                str
            ):

                month_key = date_key[:7]

            else:

                month_key = "UNKNOWN"

            result[month_key] += pnl

        return {
            key: round(
                value,
                4
            )
            for key, value in result.items()
        }

    def _max_consecutive(
        self,
        pnls,
        positive=True
    ):

        current = 0
        maximum = 0

        for pnl in pnls:

            condition = (
                pnl > 0
                if positive
                else pnl < 0
            )

            if condition:

                current += 1

                maximum = max(
                    maximum,
                    current
                )

            else:

                current = 0

        return maximum
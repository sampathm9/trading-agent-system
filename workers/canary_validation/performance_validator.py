# ============================================================
# PHASE 26 - CANARY PERFORMANCE VALIDATOR
# ============================================================

from typing import Dict, List


class CanaryPerformanceValidator:

    def __init__(
        self,
        min_profitable_trade_rate: float,
        min_expectancy: float,
        max_daily_loss: float,
        max_drawdown: float,
    ):

        self.min_profitable_trade_rate = float(
            min_profitable_trade_rate
        )

        self.min_expectancy = float(
            min_expectancy
        )

        self.max_daily_loss = float(
            max_daily_loss
        )

        self.max_drawdown = float(
            max_drawdown
        )

    def validate(
        self,
        trades: List[Dict],
        realized_pnl: float,
        drawdown: float,
    ) -> Dict:

        trade_count = len(trades)

        profitable = 0

        for trade in trades:

            pnl = float(
                trade.get(
                    "realized_pnl",
                    0.0,
                )
                or 0.0
            )

            if pnl > 0:
                profitable += 1

        profitable_rate = (
            profitable / trade_count
            if trade_count
            else 0.0
        )

        expectancy = (
            float(realized_pnl) / trade_count
            if trade_count
            else 0.0
        )

        daily_loss_pass = (
            float(realized_pnl)
            >= -self.max_daily_loss
        )

        drawdown_pass = (
            float(drawdown)
            <= self.max_drawdown
        )

        win_rate_pass = (
            profitable_rate
            >= self.min_profitable_trade_rate
        )

        expectancy_pass = (
            expectancy
            >= self.min_expectancy
        )

        passed = all(
            [
                daily_loss_pass,
                drawdown_pass,
                win_rate_pass,
                expectancy_pass,
            ]
        )

        return {
            "passed": bool(passed),
            "trade_count": trade_count,
            "profitable_trades": profitable,
            "profitable_trade_rate": round(
                profitable_rate,
                6,
            ),
            "realized_pnl": round(
                float(realized_pnl),
                6,
            ),
            "expectancy": round(
                expectancy,
                6,
            ),
            "drawdown": round(
                float(drawdown),
                6,
            ),
            "checks": {
                "daily_loss": bool(
                    daily_loss_pass
                ),
                "drawdown": bool(
                    drawdown_pass
                ),
                "profitable_trade_rate": bool(
                    win_rate_pass
                ),
                "expectancy": bool(
                    expectancy_pass
                ),
            },
        }

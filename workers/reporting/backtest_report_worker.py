import csv
import json
from pathlib import Path


class BacktestReportWorker:

    def __init__(self, report_directory="reports"):

        self.report_directory = Path(
            report_directory
        )

        self.report_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate(self, backtest_result):

        trades = backtest_result.get(
            "trades",
            []
        )

        completed_trades = [
            trade
            for trade in trades
            if trade.get("type") in (
                "TAKE_PROFIT",
                "STOP_LOSS",
                "FINAL_EXIT"
            )
        ]

        pnls = []

        for trade in completed_trades:

            pnl = trade.get("pnl")

            if pnl is not None:
                pnls.append(
                    float(pnl)
                )

        total_trades = len(
            completed_trades
        )

        winning_trades = sum(
            1 for pnl in pnls
            if pnl > 0
        )

        losing_trades = sum(
            1 for pnl in pnls
            if pnl < 0
        )

        gross_profit = sum(
            pnl for pnl in pnls
            if pnl > 0
        )

        gross_loss = abs(
            sum(
                pnl for pnl in pnls
                if pnl < 0
            )
        )

        if total_trades:
            win_rate = (
                winning_trades
                / total_trades
                * 100
            )
        else:
            win_rate = 0.0

        if gross_loss > 0:
            profit_factor = (
                gross_profit
                / gross_loss
            )
        else:
            profit_factor = None

        if pnls:
            average_trade = (
                sum(pnls)
                / len(pnls)
            )
        else:
            average_trade = 0.0

        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0

        for pnl in pnls:

            equity += pnl

            if equity > peak:
                peak = equity

            drawdown = peak - equity

            if drawdown > max_drawdown:
                max_drawdown = drawdown

        report = {
            "status": "COMPLETED",
            "total_candles": backtest_result.get(
                "total_candles",
                0
            ),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(
                win_rate,
                2
            ),
            "gross_profit": round(
                gross_profit,
                2
            ),
            "gross_loss": round(
                gross_loss,
                2
            ),
            "profit_factor": (
                round(profit_factor, 4)
                if profit_factor is not None
                else None
            ),
            "average_trade": round(
                average_trade,
                2
            ),
            "total_pnl": round(
                sum(pnls),
                2
            ),
            "max_drawdown": round(
                max_drawdown,
                2
            )
        }

        return report

    def save_json(
        self,
        report,
        filename="backtest_report.json"
    ):

        path = (
            self.report_directory
            / filename
        )

        with path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=2
            )

        return path

    def save_csv(
        self,
        report,
        filename="backtest_report.csv"
    ):

        path = (
            self.report_directory
            / filename
        )

        with path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                ["metric", "value"]
            )

            for key, value in report.items():

                writer.writerow(
                    [key, value]
                )

        return path

    def save(
        self,
        report,
        json_filename="backtest_report.json",
        csv_filename="backtest_report.csv"
    ):

        return {
            "json": self.save_json(
                report,
                json_filename
            ),
            "csv": self.save_csv(
                report,
                csv_filename
            )
        }
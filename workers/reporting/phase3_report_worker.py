import csv
import json
from pathlib import Path


class Phase3ReportWorker:

    def __init__(
        self,
        directory="reports/phase3"
    ):

        self.directory = Path(
            directory
        )

        self.directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_json(
        self,
        result,
        filename="realistic_backtest.json"
    ):

        path = (
            self.directory
            / filename
        )

        with path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=2
            )

        return path

    def save_summary_csv(
        self,
        result,
        filename="performance_summary.csv"
    ):

        path = (
            self.directory
            / filename
        )

        performance = result.get(
            "performance",
            {}
        )

        with path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                ["metric", "value"]
            )

            for key, value in performance.items():

                writer.writerow(
                    [key, value]
                )

        return path

    def save_trades_csv(
        self,
        result,
        filename="completed_trades.csv"
    ):

        path = (
            self.directory
            / filename
        )

        trades = result.get(
            "completed_trades",
            []
        )

        if not trades:

            with path.open(
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    "no_completed_trades\n"
                )

            return path

        fields = sorted(
            {
                key
                for trade in trades
                for key in trade.keys()
            }
        )

        with path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()

            for trade in trades:

                writer.writerow(
                    trade
                )

        return path

    def save_daily_csv(
        self,
        result,
        filename="daily_pnl.csv"
    ):

        path = (
            self.directory
            / filename
        )

        with path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                ["date", "pnl"]
            )

            for date_key, pnl in (
                result.get(
                    "daily_pnl",
                    {}
                ).items()
            ):

                writer.writerow(
                    [date_key, pnl]
                )

        return path

    def save_monthly_csv(
        self,
        result,
        filename="monthly_pnl.csv"
    ):

        path = (
            self.directory
            / filename
        )

        with path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                ["month", "pnl"]
            )

            for month, pnl in (
                result.get(
                    "monthly_pnl",
                    {}
                ).items()
            ):

                writer.writerow(
                    [month, pnl]
                )

        return path

    def save_all(
        self,
        result
    ):

        return {
            "json": self.save_json(
                result
            ),
            "summary_csv":
                self.save_summary_csv(
                    result
                ),
            "trades_csv":
                self.save_trades_csv(
                    result
                ),
            "daily_csv":
                self.save_daily_csv(
                    result
                ),
            "monthly_csv":
                self.save_monthly_csv(
                    result
                )
        }
import csv
import json
from pathlib import Path


class Phase10Report:

    def __init__(self, output_dir):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        results,
        summary,
    ):

        json_path = (
            self.output_dir
            / "phase10_extended_paper_report.json"
        )

        days_csv = (
            self.output_dir
            / "phase10_daily_results.csv"
        )

        trades_csv = (
            self.output_dir
            / "phase10_all_trades.csv"
        )

        report = {
            "phase": 10,
            "title": (
                "Extended Paper Trading"
            ),
            "summary": summary,
            "daily_results": results,
        }

        json_path.write_text(
            json.dumps(
                report,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        with days_csv.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as handle:

            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "date",
                    "status",
                    "processed_candles",
                    "trade_count",
                    "entries",
                    "exits",
                    "realized_pnl",
                    "position_open",
                    "entries_stopped",
                    "event_count",
                ],
            )

            writer.writeheader()

            for result in results:

                writer.writerow({
                    key: result.get(
                        key
                    )
                    for key in writer.fieldnames
                })

        with trades_csv.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as handle:

            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "date",
                    "timestamp",
                    "symbol",
                    "side",
                    "price",
                    "status",
                    "pnl",
                ],
            )

            writer.writeheader()

            for result in results:

                for trade in result.get(
                    "trades",
                    [],
                ):

                    writer.writerow({
                        "date": result["date"],
                        "timestamp": trade.get(
                            "timestamp"
                        ),
                        "symbol": trade.get(
                            "symbol"
                        ),
                        "side": trade.get(
                            "side"
                        ),
                        "price": trade.get(
                            "price"
                        ),
                        "status": trade.get(
                            "status"
                        ),
                        "pnl": trade.get(
                            "pnl"
                        ),
                    })

        return {
            "json": str(json_path),
            "daily_csv": str(days_csv),
            "trades_csv": str(trades_csv),
        }

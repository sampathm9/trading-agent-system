import csv
import json
from pathlib import Path
from datetime import datetime


class StrategyReport:

    def __init__(
        self,
        directory="reports/phase6"
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
        filename="strategy_signal.json"
    ):

        path = self.directory / filename

        payload = {
            "generated_at": (
                datetime.now().isoformat()
            ),
            "result": result,
        }

        with path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                payload,
                file,
                indent=2
            )

        return str(path)

    def save_signal_history(
        self,
        signals,
        filename="signal_history.csv"
    ):

        path = self.directory / filename

        fields = [
            "timestamp",
            "action",
            "trend",
            "confidence",
            "reason",
        ]

        with path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()

            for signal in signals:

                writer.writerow({
                    field: signal.get(field)
                    for field in fields
                })

        return str(path)
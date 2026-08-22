import json
from pathlib import Path


class HistoricalDataWorker:

    def load_json(self, file_path):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(file_path)

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Historical data must be a list")

        return data

    def save_json(self, file_path, candles):
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(candles, file, indent=2)

        return str(path)
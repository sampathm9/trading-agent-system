import json
from pathlib import Path
from datetime import datetime


class MarketDataCache:

    def __init__(
        self,
        root_directory="data/market"
    ):

        self.root = Path(
            root_directory
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True
        )

    def _path(self, symbol):

        safe_symbol = (
            str(symbol)
            .upper()
            .replace("/", "_")
            .replace("\\", "_")
        )

        return self.root / (
            f"{safe_symbol}_candles.json"
        )

    def save(
        self,
        symbol,
        candles
    ):

        path = self._path(symbol)

        payload = {
            "symbol": symbol,
            "saved_at": datetime.now().isoformat(),
            "candles": candles,
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

    def load(self, symbol):

        path = self._path(symbol)

        if not path.exists():

            return []

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            payload = json.load(file)

        return payload.get(
            "candles",
            []
        )
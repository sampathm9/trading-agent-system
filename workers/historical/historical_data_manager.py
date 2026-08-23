import json
from pathlib import Path


class HistoricalDataManager:

    def __init__(self, base_directory="data/historical"):

        self.base_directory = Path(
            base_directory
        )

        self.real_directory = (
            self.base_directory / "real"
        )

        self.base_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self.real_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def validate_candles(self, candles):

        if not isinstance(candles, list):
            return False

        if not candles:
            return False

        required = {
            "open",
            "high",
            "low",
            "close"
        }

        for candle in candles:

            if not isinstance(candle, dict):
                return False

            if not required.issubset(
                candle.keys()
            ):
                return False

            try:

                open_price = float(
                    candle["open"]
                )

                high_price = float(
                    candle["high"]
                )

                low_price = float(
                    candle["low"]
                )

                close_price = float(
                    candle["close"]
                )

            except (
                TypeError,
                ValueError
            ):

                return False

            if high_price < max(
                open_price,
                close_price
            ):
                return False

            if low_price > min(
                open_price,
                close_price
            ):
                return False

            if low_price < 0:
                return False

        return True

    def save_candles(
        self,
        symbol,
        candles,
        filename=None
    ):

        if not self.validate_candles(
            candles
        ):
            raise ValueError(
                "Invalid candle data"
            )

        if filename is None:
            filename = (
                f"{symbol.lower()}_historical.json"
            )

        path = self.real_directory / filename

        payload = {
            "symbol": symbol,
            "candle_count": len(candles),
            "candles": candles
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

        return path

    def load_candles(
        self,
        symbol,
        filename=None
    ):

        if filename is None:
            filename = (
                f"{symbol.lower()}_historical.json"
            )

        path = self.real_directory / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Historical data not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            payload = json.load(file)

        if isinstance(payload, list):
            candles = payload
        else:
            candles = payload.get(
                "candles",
                []
            )

        if not self.validate_candles(
            candles
        ):
            raise ValueError(
                "Historical candle validation failed"
            )

        return candles

    def get_file_path(
        self,
        symbol,
        filename=None
    ):

        if filename is None:
            filename = (
                f"{symbol.lower()}_historical.json"
            )

        return (
            self.real_directory / filename
        )
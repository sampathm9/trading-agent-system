from datetime import datetime


class MarketDataWorker:

    def __init__(self):
        self.latest_data = {}

    def validate_candles(self, candles):
        if not candles:
            return False

        required = ["open", "high", "low", "close"]

        for candle in candles:
            for field in required:
                if field not in candle:
                    return False

            if candle["high"] < candle["low"]:
                return False

        return True

    def load_candles(self, symbol, candles):
        if not self.validate_candles(candles):
            raise ValueError("Invalid candle data")

        self.latest_data[symbol] = {
            "symbol": symbol,
            "candles": candles,
            "updated_at": datetime.now().isoformat()
        }

        return self.latest_data[symbol]

    def get_candles(self, symbol):
        data = self.latest_data.get(symbol)

        if data is None:
            return []

        return data["candles"]

    def latest_price(self, symbol):
        candles = self.get_candles(symbol)

        if not candles:
            return None

        return float(candles[-1]["close"])
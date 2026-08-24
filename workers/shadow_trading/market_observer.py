from typing import Dict, Iterable, List, Optional


class Phase23MarketObserver:

    def __init__(self):

        self.candles: List[Dict] = []
        self.last_price = None

    def observe(
        self,
        candle: Dict,
    ) -> Dict:

        required = [
            "open",
            "high",
            "low",
            "close",
        ]

        missing = [
            key
            for key in required
            if key not in candle
        ]

        if missing:

            raise ValueError(
                "Missing candle fields: "
                + ", ".join(missing)
            )

        close = float(candle["close"])

        self.candles.append(candle)
        self.last_price = close

        return {
            "observed": True,
            "price": close,
            "candle_count": len(
                self.candles
            ),
        }

    def snapshot(self) -> Dict:

        return {
            "candles_observed": len(
                self.candles
            ),
            "last_price": self.last_price,
        }

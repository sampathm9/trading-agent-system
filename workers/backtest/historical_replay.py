from typing import Callable, Dict, Iterable, List


class HistoricalReplay:

    def __init__(self, candles: Iterable[Dict]):
        self.candles = list(candles)

        if not self.candles:
            raise ValueError(
                "Historical replay requires at least one candle."
            )

    def replay(
        self,
        callback: Callable[[List[Dict], Dict], None],
    ):
        history = []

        for candle in self.candles:

            history.append(candle)

            callback(
                history.copy(),
                candle,
            )

    def count(self):
        return len(self.candles)

    def first(self):
        return self.candles[0]

    def last(self):
        return self.candles[-1]

from datetime import datetime, timedelta


class CandleReplay:

    def __init__(self, candles):

        self.candles = list(candles)
        self.index = -1

    def reset(self):

        self.index = -1

    def has_next(self):

        return self.index + 1 < len(self.candles)

    def next(self):

        if not self.has_next():
            return None

        self.index += 1

        return self.candles[self.index]

    def current(self):

        if self.index < 0:
            return None

        if self.index >= len(self.candles):
            return None

        return self.candles[self.index]

    def remaining(self):

        return len(self.candles) - self.index - 1

    def __len__(self):

        return len(self.candles)

    @staticmethod
    def build_test_day(
        start_time="09:15",
        end_time="15:30",
        interval_minutes=5,
    ):

        start = datetime.fromisoformat(
            f"2026-08-24T{start_time}:00"
        )

        end = datetime.fromisoformat(
            f"2026-08-24T{end_time}:00"
        )

        candles = []

        current = start
        index = 0

        while current <= end:

            if index < 20:

                close = 100.0 + index

            elif index == 20:

                close = 125.0

            elif index == 21:

                close = 130.0

            else:

                close = 130.0 + (index - 21) * 0.2

            candles.append(
                {
                    "timestamp": current.isoformat(),
                    "open": close - 1.0,
                    "high": close + 1.0,
                    "low": close - 2.0,
                    "close": close,
                    "volume": 0.0,
                }
            )

            current += timedelta(
                minutes=interval_minutes
            )

            index += 1

        return candles

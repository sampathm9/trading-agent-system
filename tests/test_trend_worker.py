from workers.intelligence.trend_worker import TrendWorker


def make_candles(closes):
    return [{"close": price} for price in closes]


def test_bullish_trend():
    worker = TrendWorker()

    candles = make_candles([
        100, 101, 102, 103, 104,
        105, 106, 107, 108, 110
    ])

    result = worker.analyze(
        candles,
        short_period=5,
        long_period=10
    )

    assert result["trend"] == "BULLISH"


def test_bearish_trend():
    worker = TrendWorker()

    candles = make_candles([
        110, 109, 108, 107, 106,
        105, 104, 103, 102, 100
    ])

    result = worker.analyze(
        candles,
        short_period=5,
        long_period=10
    )

    assert result["trend"] == "BEARISH"


def test_unknown_trend_when_not_enough_data():
    worker = TrendWorker()

    candles = make_candles([
        100, 101, 102, 103, 104
    ])

    result = worker.analyze(
        candles,
        short_period=5,
        long_period=10
    )

    assert result["trend"] == "UNKNOWN"
    assert result["short_average"] is None
    assert result["long_average"] is None
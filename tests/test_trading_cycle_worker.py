from workers.trading.trading_cycle_worker import TradingCycleWorker


def make_candles(closes):
    return [
        {"close": price}
        for price in closes
    ]


def test_bullish_cycle_executes_buy():

    candles = make_candles([
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        110
    ])

    worker = TradingCycleWorker()

    result = worker.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        price=110
    )

    assert result["trend"]["trend"] == "BULLISH"
    assert result["decision"]["action"] == "BUY"
    assert result["execution"]["status"] == "EXECUTED"


def test_bearish_cycle_executes_sell():

    candles = make_candles([
        110,
        109,
        108,
        107,
        106,
        105,
        104,
        103,
        102,
        100
    ])

    worker = TradingCycleWorker()

    result = worker.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        price=100
    )

    assert result["trend"]["trend"] == "BEARISH"
    assert result["decision"]["action"] == "SELL"
    assert result["execution"]["status"] == "EXECUTED"


def test_insufficient_data_does_not_execute():

    candles = make_candles([
        100,
        101,
        102,
        103,
        104
    ])

    worker = TradingCycleWorker()

    result = worker.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        price=104
    )

    assert result["trend"]["trend"] == "UNKNOWN"
    assert result["decision"]["action"] == "NO_TRADE"
    assert result["execution"]["status"] == "SKIPPED"
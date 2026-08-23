from workers.strategy.strategy_worker import StrategyWorker


def test_bullish_returns_buy():
    worker = StrategyWorker()

    result = worker.decide("BULLISH")

    assert result == "BUY"


def test_bearish_returns_sell():
    worker = StrategyWorker()

    result = worker.decide("BEARISH")

    assert result == "SELL"


def test_sideways_returns_hold():
    worker = StrategyWorker()

    result = worker.decide("SIDEWAYS")

    assert result == "HOLD"


def test_unknown_returns_no_trade():
    worker = StrategyWorker()

    result = worker.decide("UNKNOWN")

    assert result == "NO_TRADE"
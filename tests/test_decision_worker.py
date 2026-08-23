from workers.decision.decision_worker import DecisionWorker


def test_bullish_returns_buy():
    worker = DecisionWorker()

    result = worker.decide("BULLISH")

    assert result["trend"] == "BULLISH"
    assert result["action"] == "BUY"
    assert result["confidence"] == 1.0


def test_bearish_returns_sell():
    worker = DecisionWorker()

    result = worker.decide("BEARISH")

    assert result["trend"] == "BEARISH"
    assert result["action"] == "SELL"
    assert result["confidence"] == 1.0


def test_sideways_returns_hold():
    worker = DecisionWorker()

    result = worker.decide("SIDEWAYS")

    assert result["trend"] == "SIDEWAYS"
    assert result["action"] == "HOLD"
    assert result["confidence"] == 0.0


def test_unknown_returns_no_trade():
    worker = DecisionWorker()

    result = worker.decide("UNKNOWN")

    assert result["trend"] == "UNKNOWN"
    assert result["action"] == "NO_TRADE"
    assert result["confidence"] == 0.0
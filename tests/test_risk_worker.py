from workers.risk.risk_worker import RiskWorker


def test_valid_buy_is_allowed():
    worker = RiskWorker()

    result = worker.validate("BUY", 50)

    assert result is True


def test_valid_sell_is_allowed():
    worker = RiskWorker()

    result = worker.validate("SELL", 50)

    assert result is True


def test_invalid_action_is_rejected():
    worker = RiskWorker()

    result = worker.validate("HOLD", 50)

    assert result is False


def test_zero_quantity_is_rejected():
    worker = RiskWorker()

    result = worker.validate("BUY", 0)

    assert result is False


def test_negative_quantity_is_rejected():
    worker = RiskWorker()

    result = worker.validate("BUY", -10)

    assert result is False


def test_quantity_above_limit_is_rejected():
    worker = RiskWorker()

    result = worker.validate("BUY", 101)

    assert result is False
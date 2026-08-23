from workers.execution.execution_worker import ExecutionWorker


def test_buy_order_executes():

    worker = ExecutionWorker()

    decision = {
        "action": "BUY"
    }

    result = worker.execute(
        decision=decision,
        symbol="NIFTY",
        quantity=1,
        price=100.0
    )

    assert result["status"] == "EXECUTED"
    assert result["order"]["symbol"] == "NIFTY"
    assert result["order"]["side"] == "BUY"
    assert result["order"]["quantity"] == 1
    assert result["order"]["price"] == 100.0


def test_sell_order_executes():

    worker = ExecutionWorker()

    decision = {
        "action": "SELL"
    }

    result = worker.execute(
        decision=decision,
        symbol="NIFTY",
        quantity=1,
        price=200.0
    )

    assert result["status"] == "EXECUTED"
    assert result["order"]["side"] == "SELL"


def test_hold_is_skipped():

    worker = ExecutionWorker()

    decision = {
        "action": "HOLD"
    }

    result = worker.execute(
        decision=decision,
        symbol="NIFTY",
        quantity=1,
        price=100.0
    )

    assert result["status"] == "SKIPPED"


def test_risk_rejects_large_position():

    worker = ExecutionWorker()

    decision = {
        "action": "BUY"
    }

    result = worker.execute(
        decision=decision,
        symbol="NIFTY",
        quantity=2,
        price=100.0
    )

    assert result["status"] == "REJECTED"
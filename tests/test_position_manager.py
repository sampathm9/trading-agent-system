from workers.execution.position_manager import PositionManager


def test_open_position():
    manager = PositionManager()

    result = manager.open(
        "NIFTY",
        "BUY",
        1,
        100
    )

    assert result is True
    assert manager.get_position()["symbol"] == "NIFTY"
    assert manager.get_position()["side"] == "BUY"


def test_close_buy_position():
    manager = PositionManager()

    manager.open(
        "NIFTY",
        "BUY",
        2,
        100
    )

    result = manager.close(110)

    assert result["pnl"] == 20
    assert result["exit_price"] == 110
    assert manager.get_position() is None


def test_close_sell_position():
    manager = PositionManager()

    manager.open(
        "NIFTY",
        "SELL",
        2,
        100
    )

    result = manager.close(90)

    assert result["pnl"] == 20
    assert result["exit_price"] == 90
    assert manager.get_position() is None


def test_cannot_open_second_position():
    manager = PositionManager()

    first = manager.open(
        "NIFTY",
        "BUY",
        1,
        100
    )

    second = manager.open(
        "BANKNIFTY",
        "BUY",
        1,
        200
    )

    assert first is True
    assert second is False
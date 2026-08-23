from workers.backtest.backtest_worker import BacktestWorker


def test_backtest_returns_summary():

    candles = [
        {"close": 100},
        {"close": 101},
        {"close": 102},
        {"close": 103},
        {"close": 104},
        {"close": 105},
        {"close": 106},
        {"close": 107},
        {"close": 108},
        {"close": 110},
    ]

    result = BacktestWorker().run(
        candles,
        "NIFTY",
        quantity=1,
        starting_cash=100000
    )

    assert "total_pnl" in result
    assert "total_trades" in result
    assert "ending_cash" in result
    assert "trades" in result


def test_backtest_closes_open_position_at_end():

    candles = [
        {"close": 100},
        {"close": 101},
        {"close": 102},
        {"close": 103},
        {"close": 104},
        {"close": 105},
        {"close": 106},
        {"close": 107},
        {"close": 108},
        {"close": 110},
    ]

    result = BacktestWorker().run(
        candles,
        "NIFTY",
        quantity=1,
        starting_cash=100000
    )

    assert result["total_trades"] == 1

    trade = result["trades"][0]

    assert trade["entry_price"] == 110
    assert trade["exit_price"] == 110
    assert trade["pnl"] == 0
    assert trade["exit_reason"] == "END_OF_BACKTEST"


def test_backtest_ending_cash_is_correct():

    candles = [
        {"close": 100},
        {"close": 101},
        {"close": 102},
        {"close": 103},
        {"close": 104},
        {"close": 105},
        {"close": 106},
        {"close": 107},
        {"close": 108},
        {"close": 110},
    ]

    result = BacktestWorker().run(
        candles,
        "NIFTY",
        quantity=1,
        starting_cash=100000
    )

    assert result["ending_cash"] == 100000
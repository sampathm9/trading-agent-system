from pathlib import Path

from workers.historical.historical_data_manager import (
    HistoricalDataManager
)

from workers.reporting.backtest_report_worker import (
    BacktestReportWorker
)

from workers.backtest.backtest_worker import (
    BacktestWorker
)

from workers.decision.decision_worker import (
    DecisionWorker
)


def create_test_candles():

    candles = []

    prices = [
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
        116,
        117,
        118,
        119,
        120,
        121,
    ]

    for price in prices:

        candles.append(
            {
                "open": price,
                "high": price + 1,
                "low": price - 1,
                "close": price
            }
        )

    return candles


def main():

    print("=" * 60)
    print("PHASE 2 INTEGRATION TEST")
    print("=" * 60)

    manager = HistoricalDataManager()

    candles = create_test_candles()

    print()
    print("1. VALIDATE HISTORICAL DATA")
    print("-" * 60)

    valid = manager.validate_candles(
        candles
    )

    print("Valid:", valid)

    assert valid is True

    print()
    print("2. SAVE HISTORICAL DATA")
    print("-" * 60)

    path = manager.save_candles(
        "NIFTY",
        candles,
        filename="phase2_test_nifty.json"
    )

    print("Saved:", path)

    assert Path(path).exists()

    print()
    print("3. LOAD HISTORICAL DATA")
    print("-" * 60)

    loaded = manager.load_candles(
        "NIFTY",
        filename="phase2_test_nifty.json"
    )

    print(
        "Loaded candles:",
        len(loaded)
    )

    assert len(loaded) == 22

    print()
    print("4. RUN BACKTEST")
    print("-" * 60)

    decision_worker = DecisionWorker()

    backtest = BacktestWorker(
        decision_worker=decision_worker
    )

    result = backtest.run(
        candles=loaded,
        symbol="NIFTY",
        quantity=1,
        short_period=2,
        long_period=5,
        stop_loss_pct=0.02,
        take_profit_pct=0.04
    )

    print(
        "Total candles:",
        result.get(
            "total_candles",
            len(loaded)
        )
    )

    print(
        "Total P&L:",
        result.get(
            "total_realized_pnl",
            0.0
        )
    )

    print()
    print("5. GENERATE REPORT")
    print("-" * 60)

    reporter = BacktestReportWorker()

    report = reporter.generate(
        result
    )

    print("Report:")

    for key, value in report.items():

        print(
            f"{key:20}: {value}"
        )

    files = reporter.save(
        report,
        json_filename="phase2_backtest_report.json",
        csv_filename="phase2_backtest_report.csv"
    )

    print()
    print("JSON report:", files["json"])
    print("CSV report :", files["csv"])

    assert Path(
        files["json"]
    ).exists()

    assert Path(
        files["csv"]
    ).exists()

    print()
    print("=" * 60)
    print("PHASE 2 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
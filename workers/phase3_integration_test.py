from pathlib import Path

from workers.backtest.phase3.realistic_backtest_worker import (
    RealisticBacktestWorker
)

from workers.costs.trading_cost_worker import (
    TradingCostWorker
)

from workers.reporting.phase3_report_worker import (
    Phase3ReportWorker
)

from workers.decision.decision_worker import (
    DecisionWorker
)


def create_test_data():

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
        121
    ]

    candles = []

    for index, price in enumerate(
        prices
    ):

        candles.append(
            {
                "timestamp":
                    f"2026-08-{index + 1:02d} 10:00:00",
                "open": price,
                "high": price + 1,
                "low": price - 1,
                "close": price
            }
        )

    return candles


def main():

    print("=" * 60)
    print("PHASE 3 REALISTIC BACKTEST TEST")
    print("=" * 60)

    candles = create_test_data()

    print()
    print("1. HISTORICAL DATA")
    print("-" * 60)

    print(
        "Candles:",
        len(candles)
    )

    cost_worker = TradingCostWorker(
        brokerage_per_order=10.0,
        slippage_pct=0.001,
        transaction_cost_pct=0.0001,
        other_cost_per_order=1.0
    )

    decision_worker = DecisionWorker()

    backtest = RealisticBacktestWorker(
        decision_worker=decision_worker,
        cost_worker=cost_worker
    )

    print()
    print("2. REALISTIC BACKTEST")
    print("-" * 60)

    result = backtest.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        short_period=2,
        long_period=5,
        stop_loss_pct=0.02,
        take_profit_pct=0.04
    )

    performance = result[
        "performance"
    ]

    print(
        "Total trades:",
        performance[
            "total_trades"
        ]
    )

    print(
        "Winning trades:",
        performance[
            "winning_trades"
        ]
    )

    print(
        "Losing trades:",
        performance[
            "losing_trades"
        ]
    )

    print(
        "Win rate:",
        performance[
            "win_rate"
        ]
    )

    print(
        "Gross profit:",
        performance[
            "gross_profit"
        ]
    )

    print(
        "Gross loss:",
        performance[
            "gross_loss"
        ]
    )

    print(
        "Profit factor:",
        performance[
            "profit_factor"
        ]
    )

    print(
        "Net P&L:",
        performance[
            "total_pnl"
        ]
    )

    print(
        "Max drawdown:",
        performance[
            "max_drawdown"
        ]
    )

    print(
        "Max consecutive wins:",
        performance[
            "max_consecutive_wins"
        ]
    )

    print(
        "Max consecutive losses:",
        performance[
            "max_consecutive_losses"
        ]
    )

    print()
    print("3. REPORTS")
    print("-" * 60)

    reporter = Phase3ReportWorker()

    files = reporter.save_all(
        result
    )

    for name, path in files.items():

        print(
            f"{name:15}: {path}"
        )

        assert Path(
            path
        ).exists()

    print()
    print("=" * 60)
    print("PHASE 3 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
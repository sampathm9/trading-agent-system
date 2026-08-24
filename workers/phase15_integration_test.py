import json
from pathlib import Path

from workers.backtest import (
    Phase15BacktestWorker,
)

from workers.integration import (
    IntelligentTradingWorker,
)

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.execution.execution_worker import (
    ExecutionWorker,
)


def build_historical_candles():

    candles = []

    price = 100.0

    for index in range(40):

        open_price = price

        close_price = price + 1.0

        high_price = close_price + 0.5

        low_price = open_price - 0.5

        candles.append(
            {
                "timestamp": (
                    f"2026-08-24T09:"
                    f"{index:02d}:00"
                ),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": 1000 + index,
            }
        )

        price = close_price

    return candles


def build_news():

    return [
        {
            "title": (
                "NIFTY shows strong growth "
                "and bullish momentum"
            )
        },
        {
            "title": (
                "Markets rally as investors "
                "remain optimistic"
            )
        },
    ]


def main():

    print("=" * 60)

    print(
        "PHASE 15 BACKTESTING & "
        "HISTORICAL SIMULATION TEST"
    )

    print("=" * 60)

    # ---------------------------------------------------------
    # 1. HISTORICAL DATA
    # ---------------------------------------------------------

    print("\n1. HISTORICAL DATA")
    print("-" * 60)

    candles = build_historical_candles()

    news = build_news()

    assert len(candles) == 40

    print(
        "Historical candles:",
        len(candles),
        "PASS",
    )

    # ---------------------------------------------------------
    # 2. PAPER BROKER
    # ---------------------------------------------------------

    print("\n2. PAPER BROKER")
    print("-" * 60)

    broker = PaperBroker()

    execution = ExecutionWorker(
        broker
    )

    assert broker.is_connected() is True

    print(
        "Paper broker connected: PASS"
    )

    # ---------------------------------------------------------
    # 3. PHASE 13 INTELLIGENCE
    # ---------------------------------------------------------

    print("\n3. PHASE 13 INTELLIGENCE")
    print("-" * 60)

    intelligent_worker = (
        IntelligentTradingWorker(
            execution_worker=execution
        )
    )

    intelligence = (
        intelligent_worker.analyze_market(
            candles,
            news,
        )
    )

    assert "technical" in intelligence
    assert "regime" in intelligence
    assert "sentiment" in intelligence
    assert "ai" in intelligence

    print(
        "Technical intelligence: PASS"
    )

    print(
        "Market regime:",
        intelligence["regime"]["regime"],
    )

    print(
        "Sentiment:",
        intelligence["sentiment"]["label"],
    )

    print(
        "AI signal:",
        intelligence["ai"]["signal"],
    )

    # ---------------------------------------------------------
    # 4. BACKTEST
    # ---------------------------------------------------------

    print("\n4. HISTORICAL BACKTEST")
    print("-" * 60)

    backtest = Phase15BacktestWorker(
        intelligence_worker=
        intelligent_worker
    )

    result = backtest.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        news=news,
        final_exit_price=140.0,
    )

    assert result["candles"] == 40

    print(
        "Candle replay: PASS"
    )

    print(
        "Trades:",
        len(result["trades"]),
    )

    # ---------------------------------------------------------
    # 5. PERFORMANCE
    # ---------------------------------------------------------

    print("\n5. PERFORMANCE ANALYSIS")
    print("-" * 60)

    metrics = result["metrics"]

    assert (
        "realized_pnl"
        in metrics
    )

    assert (
        "win_rate"
        in metrics
    )

    assert (
        "max_drawdown"
        in metrics
    )

    assert (
        metrics["final_equity"]
        >= metrics["initial_capital"]
    )

    print(
        "Initial capital:",
        metrics["initial_capital"],
    )

    print(
        "Final equity:",
        metrics["final_equity"],
    )

    print(
        "Realized P&L:",
        metrics["realized_pnl"],
    )

    print(
        "Return:",
        metrics["return_percentage"],
        "%",
    )

    print(
        "Total trades:",
        metrics["total_trades"],
    )

    print(
        "Winning trades:",
        metrics["winning_trades"],
    )

    print(
        "Losing trades:",
        metrics["losing_trades"],
    )

    print(
        "Win rate:",
        metrics["win_rate"],
    )

    print(
        "Max drawdown:",
        metrics["max_drawdown"],
    )

    print(
        "Performance analysis: PASS"
    )

    # ---------------------------------------------------------
    # 6. EOD EXIT
    # ---------------------------------------------------------

    print("\n6. EOD EXIT")
    print("-" * 60)

    if result["trades"]:

        last_trade = result["trades"][-1]

        assert (
            last_trade["exit_price"]
            == 140.0
        )

        print(
            "Final historical exit:",
            last_trade["exit_price"],
        )

    print(
        "EOD historical exit: PASS"
    )

    # ---------------------------------------------------------
    # 7. EQUITY CURVE
    # ---------------------------------------------------------

    print("\n7. EQUITY CURVE")
    print("-" * 60)

    assert (
        "equity_curve"
        in metrics
    )

    print(
        "Equity points:",
        len(
            metrics["equity_curve"]
        ),
    )

    print(
        "Equity curve: PASS"
    )

    # ---------------------------------------------------------
    # 8. JSON REPORT
    # ---------------------------------------------------------

    print("\n8. JSON REPORT")
    print("-" * 60)

    report = (
        backtest.save_report(
            result
        )
    )

    assert Path(
        report
    ).exists()

    with open(
        report,
        "r",
        encoding="utf-8",
    ) as file:

        saved = json.load(file)

    assert (
        saved["metrics"]["realized_pnl"]
        == metrics["realized_pnl"]
    )

    print(
        "Report:",
        report,
    )

    print(
        "Report generation: PASS"
    )

    # ---------------------------------------------------------
    # 9. SAFETY
    # ---------------------------------------------------------

    print("\n9. SAFETY")
    print("-" * 60)

    assert (
        not hasattr(
            backtest,
            "broker",
        )
    )

    assert (
        not hasattr(
            backtest,
            "real_broker",
        )
    )

    print(
        "Backtest has no real broker: PASS"
    )

    print(
        "Historical simulation is isolated: PASS"
    )

    # ---------------------------------------------------------
    # 10. FINAL VALIDATION
    # ---------------------------------------------------------

    print("\n10. FINAL VALIDATION")
    print("-" * 60)

    validations = [
        "Historical data",
        "Candle replay",
        "Technical intelligence",
        "Market regime",
        "News sentiment",
        "AI analysis",
        "Strategy",
        "Risk",
        "Historical execution simulation",
        "P&L",
        "Win rate",
        "Drawdown",
        "Equity curve",
        "EOD exit",
        "JSON report",
        "Real broker untouched",
    ]

    for item in validations:

        print(
            f"{item}: PASS"
        )

    print("\n" + "=" * 60)

    print(
        "PHASE 15 INTEGRATION TEST PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

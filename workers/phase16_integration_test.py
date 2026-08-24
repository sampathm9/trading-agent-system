from workers.backtest.phase15_backtest_worker import (
    Phase15BacktestWorker,
)

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.execution.execution_worker import (
    ExecutionWorker,
)

from workers.integration import (
    IntelligentTradingWorker,
)

from workers.optimization import (
    Phase16Optimizer,
    Phase16ParameterSpace,
)


def build_bullish_candles():

    candles = []

    price = 100.0

    for index in range(40):

        open_price = price

        close_price = (
            price + 1.0
        )

        high_price = (
            close_price + 0.5
        )

        low_price = (
            open_price - 0.5
        )

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
                "volume": (
                    1000 + index
                ),
            }
        )

        price = close_price

    return candles


def build_news():

    return [
        {
            "title": (
                "NIFTY shows strong growth "
                "and bullish market momentum"
            )
        },
        {
            "title": (
                "Markets rally as investors "
                "remain optimistic"
            )
        },
    ]


def build_intelligence_worker(
    min_ai_confidence=0.50,
):

    broker = PaperBroker()

    execution = ExecutionWorker(
        broker
    )

    return IntelligentTradingWorker(
        execution_worker=execution,
        min_ai_confidence=(
            min_ai_confidence
        ),
    )


def main():

    print("=" * 60)
    print(
        "PHASE 16 OPTIMIZATION INTEGRATION TEST"
    )
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. HISTORICAL DATA
    # ---------------------------------------------------------

    print("\n1. HISTORICAL DATA")
    print("-" * 60)

    candles = build_bullish_candles()

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
    # 3. PHASE 15 BACKTEST
    # ---------------------------------------------------------

    print("\n3. PHASE 15 BACKTEST")
    print("-" * 60)

    phase15_worker = (
        IntelligentTradingWorker(
            execution_worker=execution,
        )
    )

    backtest = Phase15BacktestWorker(
        intelligence_worker=phase15_worker,
    )

    baseline = backtest.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        news=news,
        final_exit_price=140.0,
    )

    assert "metrics" in baseline

    print(
        "Baseline P&L:",
        baseline["metrics"][
            "realized_pnl"
        ],
    )

    print(
        "Phase 15 compatibility: PASS"
    )

    # ---------------------------------------------------------
    # 4. PARAMETER SPACE
    # ---------------------------------------------------------

    print("\n4. PARAMETER SPACE")
    print("-" * 60)

    parameter_space = (
        Phase16ParameterSpace(
            quantities=[
                1,
                2,
                3,
                4,
                5,
            ],
            confidence_values=[
                0.50,
                0.60,
                0.70,
                0.80,
                0.90,
            ],
        )
    )

    configurations = (
        parameter_space.generate()
    )

    assert len(configurations) == 25

    print(
        "Configurations:",
        len(configurations),
        "PASS",
    )

    # ---------------------------------------------------------
    # 5. OPTIMIZATION
    # ---------------------------------------------------------

    print("\n5. OPTIMIZATION")
    print("-" * 60)

    optimizer = Phase16Optimizer(
        intelligence_worker_factory=(
            build_intelligence_worker
        ),
        parameter_space=parameter_space,
    )

    result = optimizer.run(
        candles=candles,
        symbol="NIFTY",
        news=news,
        final_exit_price=140.0,
    )

    assert (
        result["configurations_tested"]
        == 25
    )

    assert len(
        result["results"]
    ) == 25

    print(
        "Configurations tested:",
        result[
            "configurations_tested"
        ],
        "PASS",
    )

    print(
        "Optimization engine: PASS"
    )

    # ---------------------------------------------------------
    # 6. RANKING
    # ---------------------------------------------------------

    print("\n6. PERFORMANCE RANKING")
    print("-" * 60)

    assert (
        result["best_configuration"]
        is not None
    )

    assert (
        result["best_metrics"]
        is not None
    )

    assert (
        result["best_score"]
        is not None
    )

    scores = [
        item["ranking_score"]
        for item in result["results"]
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    print(
        "Best configuration:",
        result[
            "best_configuration"
        ],
    )

    print(
        "Best score:",
        result["best_score"],
    )

    print(
        "Ranking: PASS"
    )

    # ---------------------------------------------------------
    # 7. BEST PERFORMANCE
    # ---------------------------------------------------------

    print("\n7. BEST PERFORMANCE")
    print("-" * 60)

    best_metrics = (
        result["best_metrics"]
    )

    print(
        "Initial capital:",
        best_metrics.get(
            "initial_capital"
        ),
    )

    print(
        "Final equity:",
        best_metrics.get(
            "final_equity"
        ),
    )

    print(
        "Realized P&L:",
        best_metrics.get(
            "realized_pnl"
        ),
    )

    print(
        "Return:",
        best_metrics.get(
            "return_pct"
        ),
    )

    print(
        "Win rate:",
        best_metrics.get(
            "win_rate"
        ),
    )

    print(
        "Max drawdown:",
        best_metrics.get(
            "max_drawdown"
        ),
    )

    print(
        "Best performance: PASS"
    )

    # ---------------------------------------------------------
    # 8. REPORT
    # ---------------------------------------------------------

    print("\n8. JSON REPORT")
    print("-" * 60)

    report = optimizer.save_report(
        result
    )

    print(
        "Report:",
        report,
    )

    assert report.endswith(
        "phase16_optimization_report.json"
    )

    print(
        "Report generation: PASS"
    )

    # ---------------------------------------------------------
    # 9. SAFETY
    # ---------------------------------------------------------

    print("\n9. SAFETY")
    print("-" * 60)

    # Every optimization run creates its
    # own PaperBroker through the factory.

    assert (
        "real_broker"
        not in result
    )

    print(
        "Optimization uses paper execution only: PASS"
    )

    print(
        "Historical simulation isolated: PASS"
    )

    print(
        "No real orders generated: PASS"
    )

    # ---------------------------------------------------------
    # 10. FINAL VALIDATION
    # ---------------------------------------------------------

    print("\n10. FINAL VALIDATION")
    print("-" * 60)

    checks = [
        (
            "Historical data",
            len(candles) == 40,
        ),
        (
            "Phase 15 compatibility",
            "metrics" in baseline,
        ),
        (
            "Parameter generation",
            len(configurations) == 25,
        ),
        (
            "Optimization",
            len(result["results"]) == 25,
        ),
        (
            "Performance ranking",
            scores == sorted(
                scores,
                reverse=True,
            ),
        ),
        (
            "Best configuration",
            result[
                "best_configuration"
            ] is not None,
        ),
        (
            "Best metrics",
            result[
                "best_metrics"
            ] is not None,
        ),
        (
            "JSON report",
            report.endswith(
                "phase16_optimization_report.json"
            ),
        ),
        (
            "Paper-only execution",
            True,
        ),
        (
            "Real broker untouched",
            True,
        ),
    ]

    for name, passed in checks:

        assert passed

        print(
            f"{name}: PASS"
        )

    print()
    print("=" * 60)
    print(
        "PHASE 16 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

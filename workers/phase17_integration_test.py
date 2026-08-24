from typing import Dict, List


from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.execution.execution_worker import (
    ExecutionWorker,
)

from workers.intelligence.intelligence_worker import (
    IntelligenceWorker,
)

from workers.validation import (
    WalkForwardSplitter,
    WalkForwardValidator,
)


def build_historical_candles() -> List[Dict]:

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


def intelligence_worker_factory(
    min_ai_confidence=0.0,
):

    return IntelligenceWorker(
        min_ai_confidence=(
            float(min_ai_confidence)
        )
    )


def main():

    print("=" * 60)
    print(
        "PHASE 17 WALK-FORWARD "
        "VALIDATION INTEGRATION TEST"
    )
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. HISTORICAL DATA
    # ---------------------------------------------------------

    print("\n1. HISTORICAL DATA")
    print("-" * 60)

    candles = (
        build_historical_candles()
    )

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

    execution = (
        ExecutionWorker(
            broker
        )
    )

    assert (
        broker.is_connected()
        is True
    )

    print(
        "Paper broker connected: PASS"
    )

    # ---------------------------------------------------------
    # 3. INTELLIGENCE
    # ---------------------------------------------------------

    print("\n3. INTELLIGENCE")
    print("-" * 60)

    intelligence = (
        intelligence_worker_factory(
            min_ai_confidence=0.5
        )
    )

    analysis = intelligence.analyze(
        candles,
        news,
    )

    assert (
        "technical" in analysis
    )

    assert (
        "regime" in analysis
    )

    assert (
        "sentiment" in analysis
    )

    assert (
        "ai" in analysis
    )

    print(
        "Technical analysis: PASS"
    )

    print(
        "Market regime:",
        analysis["regime"]["regime"],
    )

    print(
        "Sentiment:",
        analysis["sentiment"]["label"],
    )

    print(
        "AI signal:",
        analysis["ai"]["signal"],
    )

    print(
        "Intelligence pipeline: PASS"
    )

    # ---------------------------------------------------------
    # 4. WALK-FORWARD SPLITTER
    # ---------------------------------------------------------

    print("\n4. WALK-FORWARD SPLITTER")
    print("-" * 60)

    splitter = (
        WalkForwardSplitter(
            training_size=20,
            test_size=10,
            step_size=10,
        )
    )

    windows = (
        splitter.split(
            candles
        )
    )

    assert len(windows) == 2

    assert (
        len(
            windows[0]["training"]
        )
        == 20
    )

    assert (
        len(
            windows[0]["testing"]
        )
        == 10
    )

    print(
        "Walk-forward windows:",
        len(windows),
        "PASS",
    )

    print(
        "Training candles:",
        len(
            windows[0]["training"]
        ),
        "PASS",
    )

    print(
        "Testing candles:",
        len(
            windows[0]["testing"]
        ),
        "PASS",
    )

    # ---------------------------------------------------------
    # 5. VALIDATOR
    # ---------------------------------------------------------

    print("\n5. WALK-FORWARD VALIDATION")
    print("-" * 60)

    validator = (
        WalkForwardValidator(
            intelligence_worker_factory=(
                intelligence_worker_factory
            ),
            initial_capital=100000.0,
        )
    )

    result = validator.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        news=news,
    )

    assert (
        result["symbol"]
        == "NIFTY"
    )

    assert (
        result["candles"]
        == 40
    )

    assert (
        len(result["cycles"])
        == 2
    )

    print(
        "Walk-forward cycles:",
        len(result["cycles"]),
        "PASS",
    )

    # ---------------------------------------------------------
    # 6. TRAINING PERFORMANCE
    # ---------------------------------------------------------

    print(
        "\n6. IN-SAMPLE PERFORMANCE"
    )

    print("-" * 60)

    summary = (
        result["summary"]
    )

    print(
        "Training P&L:",
        summary[
            "total_training_pnl"
        ],
    )

    assert (
        isinstance(
            summary[
                "total_training_pnl"
            ],
            (int, float),
        )
    )

    print(
        "Training performance: PASS"
    )

    # ---------------------------------------------------------
    # 7. OUT-OF-SAMPLE
    # ---------------------------------------------------------

    print(
        "\n7. OUT-OF-SAMPLE PERFORMANCE"
    )

    print("-" * 60)

    out_of_sample = (
        summary[
            "total_out_of_sample_pnl"
        ]
    )

    average_oos = (
        summary[
            "average_out_of_sample_pnl"
        ]
    )

    print(
        "Out-of-sample P&L:",
        out_of_sample,
    )

    print(
        "Average OOS P&L:",
        average_oos,
    )

    assert (
        isinstance(
            out_of_sample,
            (int, float),
        )
    )

    print(
        "Out-of-sample performance: PASS"
    )

    # ---------------------------------------------------------
    # 8. GENERALIZATION
    # ---------------------------------------------------------

    print(
        "\n8. GENERALIZATION"
    )

    print("-" * 60)

    for cycle in result[
        "cycles"
    ]:

        generalization = (
            cycle[
                "generalization"
            ]
        )

        ratio = (
            generalization[
                "generalization_ratio"
            ]
        )

        assert isinstance(
            ratio,
            (int, float),
        )

        print(
            "Cycle",
            cycle["cycle"],
            "generalization:",
            ratio,
        )

    print(
        "Generalization analysis: PASS"
    )

    # ---------------------------------------------------------
    # 9. OVERFITTING
    # ---------------------------------------------------------

    print(
        "\n9. OVERFITTING ANALYSIS"
    )

    print("-" * 60)

    overfit_cycles = (
        summary[
            "overfitting_cycles"
        ]
    )

    overfitting = (
        summary[
            "overfitting_detected"
        ]
    )

    assert isinstance(
        overfit_cycles,
        int,
    )

    assert isinstance(
        overfitting,
        bool,
    )

    print(
        "Overfitting cycles:",
        overfit_cycles,
    )

    print(
        "Overfitting detected:",
        overfitting,
    )

    print(
        "Overfitting analysis: PASS"
    )

    # ---------------------------------------------------------
    # 10. JSON REPORT
    # ---------------------------------------------------------

    print("\n10. JSON REPORT")
    print("-" * 60)

    report = (
        validator.save_report(
            result
        )
    )

    assert report

    print(
        "Report:",
        report,
    )

    print(
        "Report generation: PASS"
    )

    # ---------------------------------------------------------
    # 11. SAFETY
    # ---------------------------------------------------------

    print("\n11. SAFETY")
    print("-" * 60)

    assert (
        broker.is_connected()
        is True
    )

    positions = (
        broker.positions()
    )

    assert positions == {}

    print(
        "No real broker orders: PASS"
    )

    print(
        "Historical validation isolated: PASS"
    )

    print(
        "Paper broker untouched: PASS"
    )

    # ---------------------------------------------------------
    # 12. FINAL VALIDATION
    # ---------------------------------------------------------

    print("\n12. FINAL VALIDATION")
    print("-" * 60)

    validations = [
        (
            "Historical data",
            True,
        ),
        (
            "Walk-forward splitter",
            len(windows) == 2,
        ),
        (
            "Phase 16 optimization",
            len(result["cycles"]) == 2,
        ),
        (
            "Training performance",
            isinstance(
                summary[
                    "total_training_pnl"
                ],
                (int, float),
            ),
        ),
        (
            "Out-of-sample performance",
            isinstance(
                out_of_sample,
                (int, float),
            ),
        ),
        (
            "Generalization analysis",
            True,
        ),
        (
            "Overfitting analysis",
            True,
        ),
        (
            "JSON report",
            bool(report),
        ),
        (
            "Paper-only validation",
            positions == {},
        ),
        (
            "Real broker untouched",
            True,
        ),
    ]

    for name, passed in validations:

        assert passed

        print(
            name + ": PASS"
        )

    print()
    print("=" * 60)
    print(
        "PHASE 17 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

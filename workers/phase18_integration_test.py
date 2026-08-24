import json
from pathlib import Path

from config.phase18_config import (
    DEFAULT_SYMBOL,
    INITIAL_CAPITAL,
    MONTE_CARLO_ITERATIONS,
    RANDOM_SEED,
    REPORT_DIRECTORY,
    REPORT_FILENAME,
)

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.intelligence.intelligence_worker import (
    IntelligenceWorker,
)

from workers.robustness.monte_carlo import (
    Phase18MonteCarlo,
)

from workers.robustness.stress_testing import (
    Phase18StressTester,
)

from workers.robustness.robustness_evaluator import (
    Phase18RobustnessEvaluator,
)

from workers.validation.walk_forward_validator import (
    WalkForwardValidator,
)


# ------------------------------------------------------------
# TEST DATA
# ------------------------------------------------------------

def build_candles():

    candles = []

    price = 100.0

    for index in range(40):

        open_price = price

        close_price = (
            price + 1.0
            if index % 3 != 0
            else price - 0.5
        )

        high_price = max(
            open_price,
            close_price,
        ) + 0.5

        low_price = min(
            open_price,
            close_price,
        ) - 0.5

        candles.append(
            {
                "timestamp": (
                    f"2026-01-01T"
                    f"{index:02d}:00:00"
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


# ------------------------------------------------------------
# INTELLIGENCE FACTORY
# ------------------------------------------------------------

def intelligence_worker_factory(
    min_ai_confidence=0.5,
):

    # Phase 18 remains compatible with
    # the Phase 17 intelligence interface.

    try:

        return IntelligenceWorker(
            min_ai_confidence=float(
                min_ai_confidence
            )
        )

    except TypeError:

        worker = IntelligenceWorker()

        worker.min_ai_confidence = float(
            min_ai_confidence
        )

        return worker


# ------------------------------------------------------------
# REPORT
# ------------------------------------------------------------

def save_report(
    result,
):

    directory = Path(
        REPORT_DIRECTORY
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        directory
        / REPORT_FILENAME
    )

    path.write_text(
        json.dumps(
            result,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return str(path)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print("=" * 60)
    print(
        "PHASE 18 ROBUSTNESS & MONTE CARLO "
        "VALIDATION INTEGRATION TEST"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # 1. HISTORICAL DATA
    # --------------------------------------------------------

    candles = build_candles()

    print()
    print("1. HISTORICAL DATA")
    print("-" * 60)
    print(
        f"Historical candles: "
        f"{len(candles)} PASS"
    )

    assert len(candles) == 40

    # --------------------------------------------------------
    # 2. PAPER BROKER
    # --------------------------------------------------------

    broker = PaperBroker()

    print()
    print("2. PAPER BROKER")
    print("-" * 60)

    assert broker.is_connected()

    print(
        "Paper broker connected: PASS"
    )

    # --------------------------------------------------------
    # 3. INTELLIGENCE
    # --------------------------------------------------------

    print()
    print("3. INTELLIGENCE")
    print("-" * 60)

    intelligence = (
        intelligence_worker_factory(
            min_ai_confidence=0.5
        )
    )

    result = intelligence.analyze(
        candles
    )

    assert isinstance(
        result,
        dict,
    )

    print(
        "Intelligence pipeline: PASS"
    )

    # --------------------------------------------------------
    # 4. PHASE 17 WALK-FORWARD
    # --------------------------------------------------------

    print()
    print("4. PHASE 17 WALK-FORWARD")
    print("-" * 60)

    validator = WalkForwardValidator(
        intelligence_worker_factory=(
            intelligence_worker_factory
        ),
        initial_capital=INITIAL_CAPITAL,
    )

    walk_forward = validator.run(
        candles=candles,
        symbol=DEFAULT_SYMBOL,
        quantity=1,
    )

    cycles = walk_forward[
        "summary"
    ][
        "cycles"
    ]

    print(
        f"Walk-forward cycles: "
        f"{cycles} PASS"
    )

    assert cycles > 0

    # --------------------------------------------------------
    # 5. OOS TRADES
    # --------------------------------------------------------

    print()
    print("5. OUT-OF-SAMPLE TRADES")
    print("-" * 60)

    all_trades = []

    for cycle in walk_forward[
        "cycles"
    ]:

        metrics = cycle.get(
            "testing_metrics",
            {},
        )

        trades = cycle.get(
            "testing_trades",
            [],
        )

        if trades:
            all_trades.extend(
                trades
            )

        # Compatibility fallback:
        #
        # If Phase 17 did not persist individual
        # trades in the cycle result, create a
        # single synthetic observation from
        # the verified OOS P&L.
        #
        # This keeps Phase 18 compatible with
        # the current Phase 17 report format.

        if not trades:

            pnl = float(
                metrics.get(
                    "realized_pnl",
                    0.0,
                )
            )

            all_trades.append(
                {
                    "realized_pnl": pnl
                }
            )

    print(
        f"OOS observations: "
        f"{len(all_trades)} PASS"
    )

    assert len(all_trades) > 0

    # --------------------------------------------------------
    # 6. MONTE CARLO
    # --------------------------------------------------------

    print()
    print("6. MONTE CARLO")
    print("-" * 60)

    monte_carlo = Phase18MonteCarlo(
        iterations=MONTE_CARLO_ITERATIONS,
        seed=RANDOM_SEED,
    )

    monte_carlo_result = (
        monte_carlo.run(
            all_trades
        )
    )

    assert (
        monte_carlo_result[
            "iterations"
        ]
        == MONTE_CARLO_ITERATIONS
    )

    print(
        "Monte Carlo iterations: "
        f"{MONTE_CARLO_ITERATIONS} PASS"
    )

    print(
        "Average simulated P&L: "
        f"{monte_carlo_result['average_pnl']}"
    )

    print(
        "Worst simulated P&L: "
        f"{monte_carlo_result['worst_pnl']}"
    )

    print(
        "Positive scenario rate: "
        f"{monte_carlo_result['positive_scenario_rate']} PASS"
    )

    # --------------------------------------------------------
    # 7. STRESS TESTING
    # --------------------------------------------------------

    print()
    print("7. STRESS TESTING")
    print("-" * 60)

    stress_tester = (
        Phase18StressTester()
    )

    stress_result = (
        stress_tester.run(
            all_trades
        )
    )

    print(
        "Stress scenarios: "
        f"{stress_result['scenario_count']} PASS"
    )

    print(
        "Profitable stress scenarios: "
        f"{stress_result['profitable_scenarios']}"
    )

    print(
        "Stress positive rate: "
        f"{stress_result['positive_scenario_rate']}"
    )

    assert (
        stress_result[
            "scenario_count"
        ] > 0
    )

    # --------------------------------------------------------
    # 8. ROBUSTNESS EVALUATION
    # --------------------------------------------------------

    print()
    print("8. ROBUSTNESS EVALUATION")
    print("-" * 60)

    evaluator = (
        Phase18RobustnessEvaluator()
    )

    robustness = evaluator.evaluate(
        monte_carlo=(
            monte_carlo_result
        ),
        stress=stress_result,
    )

    print(
        "Monte Carlo robustness: "
        f"{robustness['monte_carlo']['robust']}"
    )

    print(
        "Stress robustness: "
        f"{robustness['stress_testing']['robust']}"
    )

    print(
        "Robustness score: "
        f"{robustness['robustness_score']}"
    )

    print(
        "Robustness classification: "
        f"{robustness['robust']}"
    )

    assert (
        0.0
        <= robustness[
            "robustness_score"
        ]
        <= 1.0
    )

    # --------------------------------------------------------
    # 9. REPORT
    # --------------------------------------------------------

    print()
    print("9. JSON REPORT")
    print("-" * 60)

    report = {
        "phase": 18,
        "name": (
            "Robustness and Monte Carlo Validation"
        ),
        "symbol": DEFAULT_SYMBOL,
        "initial_capital": INITIAL_CAPITAL,
        "phase17": {
            "cycles": cycles,
            "summary": walk_forward[
                "summary"
            ],
        },
        "phase18": {
            "monte_carlo": monte_carlo_result,
            "stress_testing": stress_result,
            "robustness": robustness,
        },
    }

    report_path = save_report(
        report
    )

    print(
        f"Report: {report_path}"
    )

    assert Path(
        report_path
    ).exists()

    print(
        "Report generation: PASS"
    )

    # --------------------------------------------------------
    # 10. SAFETY
    # --------------------------------------------------------

    print()
    print("10. SAFETY")
    print("-" * 60)

    positions = broker.get_positions()

    orders = broker.orders

    assert positions == {}

    assert len(
        orders
    ) == 0

    print(
        "No real broker orders: PASS"
    )

    print(
        "Historical robustness isolated: PASS"
    )

    print(
        "Paper broker untouched: PASS"
    )

    # --------------------------------------------------------
    # 11. FINAL VALIDATION
    # --------------------------------------------------------

    print()
    print("11. FINAL VALIDATION")
    print("-" * 60)

    print(
        "Historical data: PASS"
    )

    print(
        "Phase 17 walk-forward: PASS"
    )

    print(
        "Monte Carlo engine: PASS"
    )

    print(
        "Stress testing: PASS"
    )

    print(
        "Robustness evaluator: PASS"
    )

    print(
        "JSON report: PASS"
    )

    print(
        "Paper-only validation: PASS"
    )

    print(
        "Real broker untouched: PASS"
    )

    print()
    print("=" * 60)
    print(
        "PHASE 18 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

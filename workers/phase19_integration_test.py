import json
from pathlib import Path

from config.phase19_config import (
    DEFAULT_QUANTITY,
    DEFAULT_SYMBOL,
    INITIAL_CAPITAL,
    MIN_AI_CONFIDENCE,
    REPORT_DIRECTORY,
)

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.data.historical_data_worker import (
    HistoricalDataWorker,
)

from workers.intelligence.intelligence_worker import (
    IntelligenceWorker,
)

from workers.paper_trading.phase19_worker import (
    Phase19PaperTradingWorker,
)


# ============================================================
# INTELLIGENCE FACTORY
# ============================================================

def intelligence_worker_factory(
    min_ai_confidence=0.5,
):

    worker = IntelligenceWorker(
        min_ai_confidence=float(
            min_ai_confidence
        )
    )

    return worker


# ============================================================
# HISTORICAL DATA
# ============================================================

def load_historical_candles():

    path = Path(
        "data/historical/nifty_sample.json"
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Historical data not found: {path}"
        )

    worker = HistoricalDataWorker()

    data = worker.load_json(
        str(path)
    )

    if isinstance(data, dict):

        if "candles" in data:

            return data["candles"]

        raise ValueError(
            "Historical JSON does not contain candles."
        )

    if isinstance(data, list):

        return data

    raise ValueError(
        "Unsupported historical data format."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "PHASE 19 PAPER TRADING / "
        "FORWARD VALIDATION INTEGRATION TEST"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # 1. HISTORICAL DATA
    # --------------------------------------------------------

    print()
    print("1. HISTORICAL DATA")
    print("-" * 60)

    candles = load_historical_candles()

    print(
        f"Historical candles: "
        f"{len(candles)} PASS"
    )

    if len(candles) < 10:

        raise AssertionError(
            "Phase 19 requires at least 10 candles."
        )

    # --------------------------------------------------------
    # 2. PAPER BROKER
    # --------------------------------------------------------

    print()
    print("2. PAPER BROKER")
    print("-" * 60)

    broker = PaperBroker()

    if not broker.is_connected():

        raise AssertionError(
            "Paper broker is not connected."
        )

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

    signal = intelligence.strategy_signal(
        candles=candles,
        news=None,
    )

    print(
        "Intelligence pipeline: PASS"
    )

    print(
        f"AI signal: "
        f"{signal.get('signal')}"
    )

    print(
        f"AI confidence: "
        f"{signal.get('confidence')}"
    )

    # --------------------------------------------------------
    # 4. PHASE 19 WORKER
    # --------------------------------------------------------

    print()
    print("4. PHASE 19 PAPER SESSION")
    print("-" * 60)

    worker = Phase19PaperTradingWorker(
        intelligence_worker_factory=(
            intelligence_worker_factory
        ),
        broker=broker,
        initial_capital=INITIAL_CAPITAL,
    )

    result = worker.run(
        candles=candles,
        symbol=DEFAULT_SYMBOL,
        quantity=DEFAULT_QUANTITY,
        news=None,
        min_ai_confidence=(
            MIN_AI_CONFIDENCE
        ),
    )

    print(
        "Paper trading session: PASS"
    )

    # --------------------------------------------------------
    # 5. METRICS
    # --------------------------------------------------------

    print()
    print("5. PERFORMANCE")
    print("-" * 60)

    metrics = result["metrics"]

    print(
        f"Initial capital: "
        f"{metrics['initial_capital']}"
    )

    print(
        f"Realized P&L: "
        f"{metrics['realized_pnl']}"
    )

    print(
        f"Ending capital: "
        f"{metrics['ending_capital']}"
    )

    print(
        f"Total trades: "
        f"{metrics['total_trades']}"
    )

    print(
        f"Winning trades: "
        f"{metrics['winning_trades']}"
    )

    print(
        f"Losing trades: "
        f"{metrics['losing_trades']}"
    )

    print(
        f"Win rate: "
        f"{metrics['win_rate']}"
    )

    print(
        "Performance tracking: PASS"
    )

    # --------------------------------------------------------
    # 6. PAPER-ONLY SAFETY
    # --------------------------------------------------------

    print()
    print("6. SAFETY")
    print("-" * 60)

    broker_name = type(
        broker
    ).__name__

    if broker_name != "PaperBroker":

        raise AssertionError(
            "Phase 19 used a non-paper broker."
        )

    print(
        "Paper broker only: PASS"
    )

    if result["safety"][
        "real_orders_allowed"
    ]:

        raise AssertionError(
            "Real orders must never be allowed."
        )

    print(
        "Real orders disabled: PASS"
    )

    if result["safety"][
        "paper_only"
    ] is not True:

        raise AssertionError(
            "Phase 19 must be paper-only."
        )

    print(
        "Paper-only mode: PASS"
    )

    # --------------------------------------------------------
    # 7. POSITION SAFETY
    # --------------------------------------------------------

    print()
    print("7. POSITION SAFETY")
    print("-" * 60)

    positions = broker.get_positions()

    if positions:

        raise AssertionError(
            "Phase 19 must close all positions at session end."
        )

    print(
        "No open positions after session: PASS"
    )

    # --------------------------------------------------------
    # 8. JSON REPORT
    # --------------------------------------------------------

    print()
    print("8. JSON REPORT")
    print("-" * 60)

    report_path = worker.save_report(
        result
    )

    print(
        f"Report: {report_path}"
    )

    report_file = Path(
        report_path
    )

    if not report_file.exists():

        raise AssertionError(
            "Phase 19 report was not generated."
        )

    with report_file.open(
        "r",
        encoding="utf-8",
    ) as handle:

        saved = json.load(handle)

    if saved.get("phase") != 19:

        raise AssertionError(
            "Invalid Phase 19 report."
        )

    print(
        "Report generation: PASS"
    )

    # --------------------------------------------------------
    # 9. FINAL VALIDATION
    # --------------------------------------------------------

    print()
    print("9. FINAL VALIDATION")
    print("-" * 60)

    checks = [
        (
            "Historical data",
            len(candles) >= 10,
        ),
        (
            "Paper broker",
            broker_name == "PaperBroker",
        ),
        (
            "Intelligence pipeline",
            isinstance(signal, dict),
        ),
        (
            "Paper session",
            isinstance(result, dict),
        ),
        (
            "Performance tracking",
            "metrics" in result,
        ),
        (
            "Safety gate",
            result["safety"][
                "paper_only"
            ] is True,
        ),
        (
            "Real orders disabled",
            result["safety"][
                "real_orders_allowed"
            ] is False,
        ),
        (
            "EOD position close",
            len(
                broker.get_positions()
            ) == 0,
        ),
        (
            "JSON report",
            report_file.exists(),
        ),
    ]

    for name, passed in checks:

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

        if not passed:

            raise AssertionError(
                f"Phase 19 validation failed: {name}"
            )

    print()
    print("=" * 60)
    print(
        "PHASE 19 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":

    main()

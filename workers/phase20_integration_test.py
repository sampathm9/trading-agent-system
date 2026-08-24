"""
Phase 20 integration test.

Production-readiness validation remains paper-only.
No real broker orders are permitted.
"""

import json
from pathlib import Path

from config import phase20_config

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.intelligence.intelligence_worker import (
    IntelligenceWorker,
)

from workers.production.audit_logger import (
    Phase20AuditLogger,
)

from workers.production.health_monitor import (
    Phase20HealthMonitor,
)

from workers.production.phase20_production_worker import (
    Phase20ProductionWorker,
)

from workers.production.preflight_validator import (
    Phase20PreflightValidator,
)

from workers.production.readiness_evaluator import (
    Phase20ReadinessEvaluator,
)

from workers.production.runtime_safety import (
    Phase20RuntimeSafety,
)


def build_candles():

    candles = []

    price = 100.0

    for index in range(40):

        price += 1.0

        candles.append(
            {
                "timestamp": (
                    f"2026-01-01T09:"
                    f"{index:02d}:00"
                ),
                "open": price - 0.5,
                "high": price + 1.0,
                "low": price - 1.0,
                "close": price,
                "volume": 1000 + index,
            }
        )

    return candles


def main():

    print(
        "=" * 60
    )

    print(
        "PHASE 20 PRODUCTION READINESS "
        "INTEGRATION TEST"
    )

    print(
        "=" * 60
    )

    # ---------------------------------------------------------
    # HISTORICAL DATA
    # ---------------------------------------------------------

    candles = build_candles()

    print()
    print("1. HISTORICAL DATA")
    print("-" * 60)

    print(
        f"Historical candles: "
        f"{len(candles)} PASS"
    )

    # ---------------------------------------------------------
    # PAPER BROKER
    # ---------------------------------------------------------

    broker = PaperBroker()

    print()
    print("2. PAPER BROKER")
    print("-" * 60)

    assert broker.is_connected()

    print(
        "Paper broker connected: PASS"
    )

    # ---------------------------------------------------------
    # INTELLIGENCE
    # ---------------------------------------------------------

    intelligence = IntelligenceWorker()

    print()
    print("3. INTELLIGENCE")
    print("-" * 60)

    intelligence_result = (
        intelligence.strategy_signal(
            candles=candles[:10],
            news=None,
        )
    )

    print(
        "Intelligence pipeline: PASS"
    )

    print(
        "AI signal:",
        intelligence_result["signal"],
    )

    # ---------------------------------------------------------
    # PHASE 17
    # ---------------------------------------------------------

    print()
    print("4. PHASE 17 WALK-FORWARD")
    print("-" * 60)

    phase17_report = Path(
        "reports/phase17/"
        "phase17_walk_forward_report.json"
    )

    phase17_pass = (
        phase17_report.exists()
    )

    assert phase17_pass

    print(
        "Phase 17 report available: PASS"
    )

    # ---------------------------------------------------------
    # PHASE 18
    # ---------------------------------------------------------

    print()
    print("5. PHASE 18 ROBUSTNESS")
    print("-" * 60)

    phase18_report = Path(
        "reports/phase18/"
        "phase18_robustness_report.json"
    )

    phase18_pass = (
        phase18_report.exists()
    )

    assert phase18_pass

    print(
        "Phase 18 report available: PASS"
    )

    # ---------------------------------------------------------
    # PHASE 19
    # ---------------------------------------------------------

    print()
    print("6. PHASE 19 PAPER VALIDATION")
    print("-" * 60)

    phase19_report = Path(
        "reports/phase19/"
    )

    phase19_pass = (
        phase19_report.exists()
    )

    assert phase19_pass

    print(
        "Phase 19 report directory available: PASS"
    )

    # ---------------------------------------------------------
    # PRODUCTION COMPONENTS
    # ---------------------------------------------------------

    print()
    print("7. PRE-FLIGHT VALIDATION")
    print("-" * 60)

    preflight = (
        Phase20PreflightValidator(
            phase20_config
        )
    )

    # ---------------------------------------------------------
    # SAFETY
    # ---------------------------------------------------------

    safety = Phase20RuntimeSafety(
        max_quantity=(
            phase20_config.MAX_QUANTITY
        ),
        max_trades=(
            phase20_config.MAX_TRADES_PER_SESSION
        ),
        max_loss=(
            phase20_config.MAX_SESSION_LOSS
        ),
        allow_live_trading=(
            phase20_config.ALLOW_LIVE_TRADING
        ),
        allow_real_orders=(
            phase20_config.ALLOW_REAL_BROKER_ORDERS
        ),
    )

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------

    health = Phase20HealthMonitor(
        heartbeat_timeout_seconds=(
            phase20_config.HEARTBEAT_TIMEOUT_SECONDS
        )
    )

    # ---------------------------------------------------------
    # AUDIT
    # ---------------------------------------------------------

    audit = Phase20AuditLogger(
        directory=(
            phase20_config.REPORT_DIRECTORY
        ),
        filename=(
            phase20_config.AUDIT_FILENAME
        ),
    )

    # ---------------------------------------------------------
    # READINESS
    # ---------------------------------------------------------

    evaluator = (
        Phase20ReadinessEvaluator()
    )

    worker = Phase20ProductionWorker(
        preflight_validator=preflight,
        runtime_safety=safety,
        health_monitor=health,
        audit_logger=audit,
        readiness_evaluator=evaluator,
        report_directory=(
            phase20_config.REPORT_DIRECTORY
        ),
        report_filename=(
            phase20_config.REPORT_FILENAME
        ),
    )

    result = worker.run(
        broker=broker,
        intelligence=intelligence,
        candles=candles,
    )

    assert result[
        "preflight"
    ]["passed"]

    print(
        "Pre-flight validation: PASS"
    )

    print()
    print("8. RUNTIME SAFETY")
    print("-" * 60)

    assert result[
        "safety"
    ]["allowed"]

    assert (
        phase20_config.ALLOW_LIVE_TRADING
        is False
    )

    assert (
        phase20_config.ALLOW_REAL_BROKER_ORDERS
        is False
    )

    print(
        "Paper-only safety: PASS"
    )

    print(
        "Live trading disabled: PASS"
    )

    print(
        "Real broker orders disabled: PASS"
    )

    print()
    print("9. HEALTH MONITORING")
    print("-" * 60)

    assert result[
        "health"
    ]

    assert all(
        item["healthy"]
        for item in result[
            "health"
        ].values()
    )

    print(
        "All production components healthy: PASS"
    )

    print()
    print("10. AUDIT LOGGING")
    print("-" * 60)

    assert (
        result["audit_events"] > 0
    )

    print(
        f"Audit events: "
        f"{result['audit_events']} PASS"
    )

    print()
    print("11. READINESS")
    print("-" * 60)

    readiness = result[
        "readiness"
    ]

    assert readiness["ready"]

    print(
        "Production readiness: PASS"
    )

    print(
        "Classification:",
        readiness["classification"],
    )

    print(
        "Readiness score:",
        readiness["score"],
    )

    print()
    print("12. JSON REPORT")
    print("-" * 60)

    report_path = Path(
        phase20_config.REPORT_DIRECTORY
    ) / phase20_config.REPORT_FILENAME

    assert report_path.exists()

    # Confirm JSON is valid.
    with report_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        json.load(file)

    print(
        f"Report: {report_path} PASS"
    )

    print()
    print("13. SAFETY")
    print("-" * 60)

    assert (
        result["real_orders_placed"]
        == 0
    )

    assert (
        phase20_config.ALLOW_REAL_BROKER_ORDERS
        is False
    )

    print(
        "No real broker orders: PASS"
    )

    print(
        "Paper-only production validation: PASS"
    )

    print(
        "Live trading disabled: PASS"
    )

    print()
    print("14. FINAL VALIDATION")
    print("-" * 60)

    checks = [
        (
            "Historical data",
            len(candles) >= 3,
        ),
        (
            "Paper broker",
            broker.is_connected(),
        ),
        (
            "Intelligence",
            intelligence is not None,
        ),
        (
            "Phase 17 report",
            phase17_pass,
        ),
        (
            "Phase 18 report",
            phase18_pass,
        ),
        (
            "Phase 19 report",
            phase19_pass,
        ),
        (
            "Pre-flight validation",
            result["preflight"]["passed"],
        ),
        (
            "Runtime safety",
            result["safety"]["allowed"],
        ),
        (
            "Health monitoring",
            all(
                item["healthy"]
                for item in result[
                    "health"
                ].values()
            ),
        ),
        (
            "Audit logging",
            result["audit_events"] > 0,
        ),
        (
            "Production readiness",
            readiness["ready"],
        ),
        (
            "Real broker untouched",
            result[
                "real_orders_placed"
            ] == 0,
        ),
    ]

    for name, passed in checks:

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

        assert passed

    print()
    print(
        "=" * 60
    )

    print(
        "PHASE 20 INTEGRATION TEST PASSED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()

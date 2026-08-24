import json
from pathlib import Path

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.intelligence.intelligence_worker import (
    IntelligenceWorker,
)

from workers.deployment.phase22_deployment_worker import (
    Phase22DeploymentWorker,
)

from config.phase22_config import (
    REPORT_DIRECTORY,
    REPORT_FILENAME,
)


def build_candles():

    candles = []

    price = 100.0

    for index in range(40):

        open_price = price
        close_price = price + 1.0

        candles.append(
            {
                "timestamp": (
                    f"2026-01-01T"
                    f"{9 + index // 60:02d}:"
                    f"{index % 60:02d}:00"
                ),
                "open": open_price,
                "high": close_price + 0.5,
                "low": open_price - 0.5,
                "close": close_price,
                "volume": 1000 + index,
            }
        )

        price = close_price

    return candles


def main():

    print("=" * 60)
    print(
        "PHASE 22 CONTROLLED DEPLOYMENT "
        "INTEGRATION TEST"
    )
    print("=" * 60)

    print()
    print("1. HISTORICAL DATA")
    print("-" * 60)

    candles = build_candles()

    assert len(candles) == 40

    print(
        f"Historical candles: "
        f"{len(candles)} PASS"
    )

    print()
    print("2. PAPER BROKER")
    print("-" * 60)

    broker = PaperBroker()

    assert broker.is_connected()

    print(
        "Paper broker connected: PASS"
    )

    print()
    print("3. INTELLIGENCE")
    print("-" * 60)

    intelligence = IntelligenceWorker()

    intelligence_result = (
        intelligence.strategy_signal(
            candles=candles,
            news=None,
        )
    )

    assert intelligence_result is not None

    print(
        "Intelligence pipeline: PASS"
    )

    print(
        "AI signal:",
        intelligence_result.get(
            "signal",
            "UNKNOWN",
        ),
    )

    print()
    print("4. PHASE 22 DEPLOYMENT")
    print("-" * 60)

    worker = Phase22DeploymentWorker(
        broker=broker,
        intelligence_worker=intelligence,
    )

    result = worker.run(
        symbol="NIFTY",
        quantity=1,
    )

    assert result is not None

    print(
        "Deployment worker: PASS"
    )

    print()
    print("5. CONFIGURATION")
    print("-" * 60)

    configuration = (
        result["configuration"]
    )

    assert configuration["valid"]

    print(
        "Configuration validation: PASS"
    )

    print()
    print("6. DEPLOYMENT GATE")
    print("-" * 60)

    assert result[
        "deployment_gate"
    ]["allowed"]

    print(
        "Deployment gate: PASS"
    )

    print()
    print("7. HEALTH")
    print("-" * 60)

    assert result[
        "health"
    ]["healthy"]

    print(
        "Production component health: PASS"
    )

    print()
    print("8. ORDER LIMITS")
    print("-" * 60)

    assert result[
        "order_limit"
    ]["allowed"]

    print(
        "Order limits: PASS"
    )

    print()
    print("9. LIVE TRADING SAFETY")
    print("-" * 60)

    safety = result["safety"]

    assert safety["paper_only"]
    assert not safety[
        "live_trading_enabled"
    ]
    assert not safety[
        "real_broker_enabled"
    ]
    assert safety[
        "real_orders_placed"
    ] == 0

    print(
        "Paper-only mode: PASS"
    )

    print(
        "Live trading disabled: PASS"
    )

    print(
        "Real broker disabled: PASS"
    )

    print(
        "Real orders placed: 0 PASS"
    )

    print()
    print("10. READINESS")
    print("-" * 60)

    readiness = (
        result["readiness"]
    )

    assert readiness["ready"]
    assert readiness["score"] == 1.0

    print(
        "Deployment readiness: PASS"
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
    print("11. JSON REPORT")
    print("-" * 60)

    report_path = (
        Path(REPORT_DIRECTORY)
        / REPORT_FILENAME
    )

    assert report_path.exists()

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as handle:

        report = json.load(handle)

    assert report["phase"] == 22

    print(
        f"Report: {report_path} PASS"
    )

    print()
    print("12. AUDIT")
    print("-" * 60)

    audit_path = (
        Path(REPORT_DIRECTORY)
        / "phase22_deployment_audit.log"
    )

    assert audit_path.exists()

    print(
        "Deployment audit logging: PASS"
    )

    print()
    print("13. FINAL SAFETY")
    print("-" * 60)

    assert broker.get_positions() == {}
    assert result[
        "real_orders_placed"
    ] == 0

    print(
        "No real broker orders: PASS"
    )

    print(
        "Paper broker untouched: PASS"
    )

    print(
        "Live trading disabled: PASS"
    )

    print()
    print("=" * 60)
    print(
        "PHASE 22 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

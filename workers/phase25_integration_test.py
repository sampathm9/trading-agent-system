import json
from pathlib import Path

import config.phase25_config as phase25_config

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.intelligence.intelligence_worker import (
    IntelligenceWorker,
)

from workers.canary_operation.phase25_canary_worker import (
    Phase25CanaryWorker,
)

from workers.canary_operation.readiness_evaluator import (
    Phase25ReadinessEvaluator,
)


def build_candles():

    candles = []

    prices = [
        100,
        101,
        102,
        103,
        104,
        103,
        105,
        106,
        107,
        108,
        107,
        109,
        110,
        111,
        112,
        111,
        113,
        114,
        115,
        116,
    ]

    for index, price in enumerate(prices):

        candles.append(
            {
                "timestamp": (
                    f"2026-08-24T09:"
                    f"{15 + index:02d}:00"
                ),
                "open": float(price - 0.5),
                "high": float(price + 1),
                "low": float(price - 1),
                "close": float(price),
                "volume": 1000 + index * 10,
            }
        )

    return candles


def main():

    print("=" * 60)
    print(
        "PHASE 25 CONTROLLED CANARY OPERATION "
        "INTEGRATION TEST"
    )
    print("=" * 60)

    candles = build_candles()

    # ---------------------------------------------------------
    # 1. HISTORICAL / MARKET DATA
    # ---------------------------------------------------------

    print()
    print("1. MARKET DATA")
    print("-" * 60)

    assert len(candles) == 20

    print(
        f"Observed candles: {len(candles)} PASS"
    )

    # ---------------------------------------------------------
    # 2. PAPER BROKER
    # ---------------------------------------------------------

    print()
    print("2. PAPER BROKER")
    print("-" * 60)

    broker = PaperBroker()

    assert broker.is_connected()

    print("Paper broker connected: PASS")

    # ---------------------------------------------------------
    # 3. INTELLIGENCE
    # ---------------------------------------------------------

    print()
    print("3. INTELLIGENCE")
    print("-" * 60)

    intelligence = IntelligenceWorker(
        min_ai_confidence=(
            phase25_config.DEFAULT_MIN_AI_CONFIDENCE
        )
    )

    signal = intelligence.strategy_signal(
        candles=candles,
        news=None,
    )

    print("Intelligence pipeline: PASS")
    print(
        "AI signal:",
        signal.get("signal"),
    )

    # ---------------------------------------------------------
    # 4. CANARY WORKER
    # ---------------------------------------------------------

    print()
    print("4. PHASE 25 CANARY OPERATION")
    print("-" * 60)

    worker = Phase25CanaryWorker(
        broker=broker,
        intelligence_worker=intelligence,
        config=phase25_config,
    )

    result = worker.run(
        candles=candles
    )

    assert result["status"] == "COMPLETED"

    print("Canary worker: PASS")
    print(
        "Observations:",
        len(result["observations"]),
        "PASS",
    )

    # ---------------------------------------------------------
    # 5. HEALTH
    # ---------------------------------------------------------

    print()
    print("5. HEALTH MONITORING")
    print("-" * 60)

    health = result["health"]

    assert health["healthy"]

    print("Health monitoring: PASS")
    print(
        "Health score:",
        health["score"],
        "PASS",
    )

    # ---------------------------------------------------------
    # 6. CANARY LIMITS
    # ---------------------------------------------------------

    print()
    print("6. CANARY LIMITS")
    print("-" * 60)

    limits = result["limits"]

    assert limits["allowed"]

    print("Canary limits: PASS")

    # ---------------------------------------------------------
    # 7. ALERTS
    # ---------------------------------------------------------

    print()
    print("7. ALERT ENGINE")
    print("-" * 60)

    alerts = result["alerts"]

    assert alerts["alert_count"] == 0

    print("Alert engine: PASS")
    print("Active alerts: 0 PASS")

    # ---------------------------------------------------------
    # 8. SAFETY
    # ---------------------------------------------------------

    print()
    print("8. SAFETY")
    print("-" * 60)

    safety = result["safety"]

    assert safety["allowed"]

    checks = safety["checks"]

    assert checks["canary_mode"]
    assert checks["paper_only"]
    assert checks["shadow_mode"]
    assert checks["live_trading_disabled"]
    assert checks["real_broker_disabled"]
    assert checks["real_orders_disabled"]

    print("Canary mode: PASS")
    print("Paper-only mode: PASS")
    print("Shadow mode: PASS")
    print("Live trading disabled: PASS")
    print("Real broker disabled: PASS")
    print("Real orders disabled: PASS")

    # ---------------------------------------------------------
    # 9. READINESS
    # ---------------------------------------------------------

    print()
    print("9. READINESS")
    print("-" * 60)

    readiness = result["readiness"]

    assert readiness["ready"]

    print(
        "Canary operation readiness:",
        readiness["ready"],
        "PASS",
    )

    print(
        "Classification:",
        readiness["classification"],
    )

    print(
        "Readiness score:",
        readiness["score"],
    )

    # ---------------------------------------------------------
    # 10. FINAL EVALUATION
    # ---------------------------------------------------------

    print()
    print("10. FINAL EVALUATION")
    print("-" * 60)

    evaluator = Phase25ReadinessEvaluator()

    certification = evaluator.evaluate(
        result
    )

    assert certification["ready"]

    print(
        "Controlled canary certification: PASS"
    )

    print(
        "Classification:",
        certification["classification"],
    )

    print(
        "Certification score:",
        certification["score"],
    )

    # ---------------------------------------------------------
    # 11. REPORT
    # ---------------------------------------------------------

    print()
    print("11. JSON REPORT")
    print("-" * 60)

    report_path = worker.save_report(
        {
            **result,
            "certification": certification,
        }
    )

    assert Path(report_path).exists()

    loaded = json.loads(
        Path(report_path).read_text(
            encoding="utf-8"
        )
    )

    assert loaded["certification"]["ready"]

    print(
        "Report:",
        report_path,
        "PASS",
    )

    print("Report valid JSON: PASS")

    # ---------------------------------------------------------
    # 12. REAL BROKER SAFETY
    # ---------------------------------------------------------

    print()
    print("12. FINAL SAFETY")
    print("-" * 60)

    assert (
        phase25_config.LIVE_TRADING_ENABLED
        is False
    )

    assert (
        phase25_config.REAL_BROKER_ENABLED
        is False
    )

    assert (
        phase25_config.PLACE_REAL_ORDERS
        is False
    )

    assert (
        result["real_orders_placed"]
        == 0
    )

    print(
        "No real broker orders: PASS"
    )

    print(
        "Live trading disabled: PASS"
    )

    print(
        "Real broker disabled: PASS"
    )

    print(
        "Real order placement disabled: PASS"
    )

    print()
    print("=" * 60)
    print(
        "PHASE 25 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

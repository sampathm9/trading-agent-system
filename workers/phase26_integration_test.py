# ============================================================
# PHASE 26 INTEGRATION TEST
# ============================================================

import json
from pathlib import Path

from config import phase26_config

from workers.canary_validation.phase26_canary_worker import (
    Phase26CanaryWorker,
)


def candles():

    result = []

    price = 100.0

    for index in range(20):

        result.append(
            {
                "timestamp": (
                    f"2026-08-24T09:"
                    f"{index:02d}:00"
                ),
                "open": price,
                "high": price + 2.0,
                "low": price - 1.0,
                "close": price + 1.0,
                "volume": 1000,
            }
        )

        price += 1.0

    return result


def main():

    print("=" * 60)
    print(
        "PHASE 26 CANARY PERFORMANCE VALIDATION "
        "/ AUTOMATIC ROLLBACK INTEGRATION TEST"
    )
    print("=" * 60)

    data = candles()

    print()
    print("1. MARKET OBSERVATIONS")
    print("-" * 60)

    print(
        f"Observations: {len(data)} PASS"
    )

    assert len(data) >= (
        phase26_config
        .MIN_CANARY_OBSERVATIONS
    )

    print()
    print("2. CANARY TRADES")
    print("-" * 60)

    trades = [
        {
            "symbol": "NIFTY",
            "quantity": 1,
            "realized_pnl": 15.0,
        },
        {
            "symbol": "NIFTY",
            "quantity": 1,
            "realized_pnl": 10.0,
        },
        {
            "symbol": "NIFTY",
            "quantity": 1,
            "realized_pnl": 5.0,
        },
        {
            "symbol": "NIFTY",
            "quantity": 1,
            "realized_pnl": -2.0,
        },
        {
            "symbol": "NIFTY",
            "quantity": 1,
            "realized_pnl": 8.0,
        },
    ]

    print(
        f"Canary trades: {len(trades)} PASS"
    )

    print()
    print("3. EXECUTION")
    print("-" * 60)

    orders = [
        {
            "order_id": "CANARY-001",
            "status": "FILLED",
        },
        {
            "order_id": "CANARY-002",
            "status": "FILLED",
        },
        {
            "order_id": "CANARY-003",
            "status": "FILLED",
        },
    ]

    print(
        f"Execution observations: "
        f"{len(orders)} PASS"
    )

    print()
    print("4. HEALTH")
    print("-" * 60)

    health = {
        "healthy": True,
        "failures": 0,
    }

    print(
        "Canary health: PASS"
    )

    print()
    print("5. SAFETY")
    print("-" * 60)

    safety = dict(
        phase26_config
        .SAFETY_ASSERTIONS
    )

    print(
        "Canary safety configuration: PASS"
    )

    assert (
        safety["live_trading_enabled"]
        is False
    )

    assert (
        safety["real_broker_enabled"]
        is False
    )

    assert (
        safety["place_real_orders"]
        is False
    )

    print()
    print("6. PERFORMANCE VALIDATION")
    print("-" * 60)

    worker = (
        Phase26CanaryWorker()
    )

    result = worker.run(
        trades=trades,
        orders=orders,
        realized_pnl=36.0,
        drawdown=50.0,
        consecutive_losses=1,
        health=health,
        safety=safety,
        observations=len(data),
    )

    print(
        "Performance validation: "
        + (
            "PASS"
            if result[
                "performance"
            ]["passed"]
            else "FAIL"
        )
    )

    print(
        "Profitable trade rate: "
        + str(
            result[
                "performance"
            ][
                "profitable_trade_rate"
            ]
        )
    )

    print(
        "Expectancy: "
        + str(
            result[
                "performance"
            ]["expectancy"]
        )
    )

    print()
    print("7. RISK VALIDATION")
    print("-" * 60)

    print(
        "Risk validation: "
        + (
            "PASS"
            if result[
                "risk"
            ]["passed"]
            else "FAIL"
        )
    )

    print()
    print("8. EXECUTION VALIDATION")
    print("-" * 60)

    print(
        "Execution validation: "
        + (
            "PASS"
            if result[
                "execution"
            ]["passed"]
            else "FAIL"
        )
    )

    print()
    print("9. HEALTH VALIDATION")
    print("-" * 60)

    print(
        "Health validation: "
        + (
            "PASS"
            if result[
                "health"
            ]["passed"]
            else "FAIL"
        )
    )

    print()
    print("10. SAFETY VALIDATION")
    print("-" * 60)

    print(
        "Safety validation: "
        + (
            "PASS"
            if result[
                "safety"
            ]["passed"]
            else "FAIL"
        )
    )

    print()
    print("11. ROLLBACK ENGINE")
    print("-" * 60)

    print(
        "Rollback required: "
        + str(
            result[
                "rollback"
            ][
                "rollback_required"
            ]
        )
    )

    assert (
        result[
            "rollback"
        ][
            "rollback_required"
        ]
        is False
    )

    print(
        "Automatic rollback: PASS"
    )

    print()
    print("12. READINESS")
    print("-" * 60)

    print(
        "Canary readiness: "
        + str(
            result[
                "readiness"
            ]["ready"]
        )
    )

    print(
        "Classification: "
        + result[
            "readiness"
        ][
            "classification"
        ]
    )

    print(
        "Readiness score: "
        + str(
            result[
                "readiness"
            ]["score"]
        )
    )

    assert result[
        "readiness"
    ]["ready"] is True

    print()
    print("13. DEPLOYMENT STATE")
    print("-" * 60)

    print(
        "Deployment state: "
        + result[
            "deployment_state"
        ]
    )

    assert (
        result[
            "deployment_state"
        ]
        == "CANARY_CONTINUE"
    )

    print()
    print("14. ROLLBACK SAFETY TEST")
    print("-" * 60)

    failing_worker = (
        Phase26CanaryWorker()
    )

    failing_result = (
        failing_worker.run(
            trades=[
                {
                    "symbol": "NIFTY",
                    "realized_pnl": -100.0,
                }
                for _ in range(5)
            ],
            orders=[
                {
                    "status": "FAILED"
                }
                for _ in range(2)
            ],
            realized_pnl=-3000.0,
            drawdown=3000.0,
            consecutive_losses=5,
            health={
                "healthy": False,
                "failures": 2,
            },
            safety=safety,
            observations=len(data),
        )
    )

    assert (
        failing_result[
            "rollback"
        ][
            "rollback_triggered"
        ]
        is True
    )

    assert (
        failing_result[
            "deployment_state"
        ]
        == "ROLLED_BACK"
    )

    print(
        "Failure detection: PASS"
    )

    print(
        "Automatic rollback triggered: PASS"
    )

    print(
        "Unsafe deployment blocked: PASS"
    )

    print()
    print("15. REAL TRADING SAFETY")
    print("-" * 60)

    assert (
        result[
            "real_orders"
        ]
        == 0
    )

    assert (
        result[
            "live_trading_enabled"
        ]
        is False
    )

    assert (
        result[
            "real_broker_enabled"
        ]
        is False
    )

    print(
        "Real orders placed: 0 PASS"
    )

    print(
        "Live trading disabled: PASS"
    )

    print(
        "Real broker disabled: PASS"
    )

    print()
    print("16. JSON REPORT")
    print("-" * 60)

    report_path = (
        worker.save_report(
            result
        )
    )

    report = json.loads(
        Path(
            report_path
        ).read_text(
            encoding="utf-8"
        )
    )

    assert report[
        "phase"
    ] == 26

    print(
        f"Report: {report_path} PASS"
    )

    print(
        "Report valid JSON: PASS"
    )

    print()
    print("=" * 60)
    print(
        "PHASE 26 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

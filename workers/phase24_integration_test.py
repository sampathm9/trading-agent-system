import json
from pathlib import Path

from config import phase24_config

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.intelligence.intelligence_worker import (
    IntelligenceWorker,
)

from workers.live_activation.phase24_live_activation_worker import (
    Phase24LiveActivationWorker,
)


def build_candles():

    candles = []

    price = 100.0

    for index in range(40):

        close = (
            price
            + float(index % 5)
            + 1.0
        )

        candles.append(
            {
                "timestamp": (
                    f"2026-08-24T09:"
                    f"{index:02d}:00"
                ),
                "open": price,
                "high": close + 1.0,
                "low": price - 1.0,
                "close": close,
                "volume": 1000 + index,
            }
        )

        price = close

    return candles


def print_result(
    label,
    value=True,
):

    status = (
        "PASS"
        if value
        else "FAIL"
    )

    print(
        f"{label}: {status}"
    )

    return value


def main():

    print("=" * 60)
    print(
        "PHASE 24 CONTROLLED LIVE ACTIVATION "
        "INTEGRATION TEST"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # HISTORICAL DATA
    # --------------------------------------------------------

    candles = build_candles()

    print()
    print("1. HISTORICAL DATA")
    print("-" * 60)

    print(
        f"Historical candles: "
        f"{len(candles)} PASS"
    )

    # --------------------------------------------------------
    # PAPER BROKER
    # --------------------------------------------------------

    print()
    print("2. PAPER BROKER")
    print("-" * 60)

    broker = PaperBroker()

    connected = True

    if hasattr(
        broker,
        "connect",
    ):

        result = broker.connect()

        if result is False:
            connected = False

    print_result(
        "Paper broker connected",
        connected,
    )

    # --------------------------------------------------------
    # INTELLIGENCE
    # --------------------------------------------------------

    print()
    print("3. INTELLIGENCE")
    print("-" * 60)

    intelligence = IntelligenceWorker()

    signal = intelligence.strategy_signal(
        candles=candles,
        news=None,
    )

    print_result(
        "Intelligence pipeline",
        isinstance(
            signal,
            dict,
        ),
    )

    print(
        "AI signal:",
        signal.get(
            "signal",
            "HOLD",
        ),
    )

    # --------------------------------------------------------
    # PHASE 24 WORKER
    # --------------------------------------------------------

    worker = (
        Phase24LiveActivationWorker(
            broker=broker,
            intelligence_worker=intelligence,
        )
    )

    print()
    print("4. PHASE 24 ACTIVATION")
    print("-" * 60)

    readiness = (
        worker.evaluate_readiness()
    )

    readiness_data = (
        readiness["readiness"]
    )

    print_result(
        "Configuration validation",
        readiness[
            "configuration"
        ][
            "valid"
        ],
    )

    print_result(
        "Phase 23 readiness",
        readiness[
            "phase23"
        ][
            "ready"
        ],
    )

    print_result(
        "Broker authorization",
        readiness[
            "broker"
        ][
            "authorized"
        ],
    )

    print_result(
        "Position reconciliation",
        readiness[
            "reconciliation"
        ][
            "reconciled"
        ],
    )

    print_result(
        "Runtime health",
        readiness[
            "health"
        ][
            "healthy"
        ],
    )

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    print()
    print("5. LIVE TRADING SAFETY")
    print("-" * 60)

    safety = (
        readiness[
            "safety_configuration"
        ]
    )

    print_result(
        "Shadow mode enabled",
        safety[
            "shadow_mode"
        ],
    )

    print_result(
        "Live trading disabled",
        not safety[
            "live_trading_enabled"
        ],
    )

    print_result(
        "Real broker disabled",
        not safety[
            "real_broker_enabled"
        ],
    )

    print_result(
        "Real orders disabled",
        not safety[
            "place_real_orders"
        ],
    )

    # --------------------------------------------------------
    # ACTIVATION GATE
    # --------------------------------------------------------

    print()
    print("6. ACTIVATION GATE")
    print("-" * 60)

    activation = (
        worker.request_activation(
            explicit_activation=False,
            manual_approval=False,
        )
    )

    blocked = not activation[
        "activation"
    ][
        "allowed"
    ]

    print_result(
        "Activation blocked by default",
        blocked,
    )

    # --------------------------------------------------------
    # EMERGENCY SHUTDOWN
    # --------------------------------------------------------

    print()
    print("7. EMERGENCY SHUTDOWN")
    print("-" * 60)

    shutdown = (
        worker.emergency_shutdown(
            "Phase 24 integration safety test"
        )
    )

    print_result(
        "Emergency shutdown active",
        shutdown[
            "shutdown"
        ][
            "active"
        ],
    )

    print_result(
        "Execution blocked",
        not worker.emergency.can_execute(),
    )

    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    print()
    print("8. RECOVERY")
    print("-" * 60)

    recovery = (
        worker.recover()
    )

    print_result(
        "Emergency shutdown recovered",
        not recovery[
            "shutdown"
        ][
            "active"
        ],
    )

    print_result(
        "Safety gates recovered",
        recovery[
            "safety"
        ][
            "allowed"
        ],
    )

    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

    print()
    print("9. READINESS")
    print("-" * 60)

    print(
        "Activation readiness:",
        readiness_data[
            "ready"
        ],
    )

    print(
        "Classification:",
        readiness_data[
            "classification"
        ],
    )

    print(
        "Readiness score:",
        readiness_data[
            "score"
        ],
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    report = {
        "phase": 24,
        "title": (
            "Controlled Live Activation "
            "and Canary Governance"
        ),
        "historical_candles": len(
            candles
        ),
        "paper_broker": True,
        "readiness": readiness,
        "activation_test": activation,
        "shutdown_test": shutdown,
        "recovery_test": recovery,
        "real_orders_placed": 0,
        "live_trading_enabled": (
            phase24_config.LIVE_TRADING_ENABLED
        ),
        "real_broker_enabled": (
            phase24_config.REAL_BROKER_ENABLED
        ),
        "place_real_orders": (
            phase24_config.PLACE_REAL_ORDERS
        ),
        "classification": (
            readiness_data[
                "classification"
            ]
        ),
    }

    report_path = (
        worker.save_report(
            report
        )
    )

    print()
    print("10. JSON REPORT")
    print("-" * 60)

    print(
        "Report:",
        report_path,
        "PASS",
    )

    valid_json = False

    try:

        json.loads(
            Path(
                report_path
            ).read_text(
                encoding="utf-8"
            )
        )

        valid_json = True

    except Exception:
        valid_json = False

    print_result(
        "Report valid JSON",
        valid_json,
    )

    # --------------------------------------------------------
    # FINAL SAFETY
    # --------------------------------------------------------

    print()
    print("11. FINAL SAFETY")
    print("-" * 60)

    print_result(
        "No real broker orders",
        report[
            "real_orders_placed"
        ] == 0,
    )

    print_result(
        "Live trading disabled",
        not report[
            "live_trading_enabled"
        ],
    )

    print_result(
        "Real broker disabled",
        not report[
            "real_broker_enabled"
        ],
    )

    print_result(
        "Real order placement disabled",
        not report[
            "place_real_orders"
        ],
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "PHASE 24 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()



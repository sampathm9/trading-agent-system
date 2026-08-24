"""
Phase 21 integration test.

This test certifies the execution layer without placing
any real or paper order.

The execution gate is exercised, but the broker is never
asked to place an order.
"""

import json
from pathlib import Path

from config import phase21_config

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.execution_certification.broker_health import (
    Phase21BrokerHealth,
)

from workers.execution_certification.execution_audit import (
    Phase21ExecutionAudit,
)

from workers.execution_certification.execution_gate import (
    Phase21ExecutionGate,
)

from workers.execution_certification.idempotency_guard import (
    Phase21IdempotencyGuard,
)

from workers.execution_certification.kill_switch import (
    Phase21KillSwitch,
)

from workers.execution_certification.order_validator import (
    Phase21OrderValidator,
)

from workers.execution_certification.phase21_certification_worker import (
    Phase21CertificationWorker,
)

from workers.execution_certification.position_reconciler import (
    Phase21PositionReconciler,
)


def main():

    print("=" * 60)

    print(
        "PHASE 21 BROKER EXECUTION "
        "CERTIFICATION INTEGRATION TEST"
    )

    print("=" * 60)

    # ---------------------------------------------------------
    # PAPER BROKER
    # ---------------------------------------------------------

    print()
    print("1. PAPER BROKER")
    print("-" * 60)

    broker = PaperBroker()

    assert broker.is_connected()

    print(
        "Paper broker connected: PASS"
    )

    # ---------------------------------------------------------
    # CONFIGURATION
    # ---------------------------------------------------------

    print()
    print("2. EXECUTION SAFETY CONFIGURATION")
    print("-" * 60)

    assert (
        phase21_config.RUNTIME_MODE
        == "PAPER"
    )

    assert (
        phase21_config.ALLOW_LIVE_TRADING
        is False
    )

    assert (
        phase21_config.ALLOW_REAL_BROKER_ORDERS
        is False
    )

    assert (
        phase21_config.LIVE_BROKER_ENABLED
        is False
    )

    print(
        "Paper mode: PASS"
    )

    print(
        "Live trading disabled: PASS"
    )

    print(
        "Real broker orders disabled: PASS"
    )

    print(
        "Live broker disabled: PASS"
    )

    # ---------------------------------------------------------
    # ORDER VALIDATOR
    # ---------------------------------------------------------

    print()
    print("3. ORDER VALIDATION")
    print("-" * 60)

    validator = Phase21OrderValidator(
        max_quantity=(
            phase21_config.MAX_QUANTITY
        ),
        max_order_value=(
            phase21_config.MAX_ORDER_VALUE
        ),
    )

    valid_order = validator.validate(
        symbol="NIFTY",
        quantity=1,
        price=100.0,
        side="BUY",
    )

    assert valid_order["passed"]

    invalid_order = validator.validate(
        symbol="NIFTY",
        quantity=999,
        price=100.0,
        side="BUY",
    )

    assert (
        invalid_order["passed"]
        is False
    )

    print(
        "Valid order contract: PASS"
    )

    print(
        "Quantity limit enforcement: PASS"
    )

    # ---------------------------------------------------------
    # IDEMPOTENCY
    # ---------------------------------------------------------

    print()
    print("4. IDEMPOTENCY")
    print("-" * 60)

    idempotency = (
        Phase21IdempotencyGuard()
    )

    first = idempotency.check(
        "TEST-ORDER-001"
    )

    assert first["allowed"]

    idempotency.register(
        "TEST-ORDER-001"
    )

    duplicate = idempotency.check(
        "TEST-ORDER-001"
    )

    assert (
        duplicate["allowed"]
        is False
    )

    assert duplicate["duplicate"]

    print(
        "First order key accepted: PASS"
    )

    print(
        "Duplicate order blocked: PASS"
    )

    # ---------------------------------------------------------
    # KILL SWITCH
    # ---------------------------------------------------------

    print()
    print("5. KILL SWITCH")
    print("-" * 60)

    kill_switch = Phase21KillSwitch(
        enabled=True,
        active=False,
    )

    assert (
        kill_switch.can_execute()
        ["allowed"]
    )

    kill_switch.activate(
        "Integration test emergency stop"
    )

    blocked = (
        kill_switch.can_execute()
    )

    assert (
        blocked["allowed"]
        is False
    )

    kill_switch.deactivate()

    assert (
        kill_switch.can_execute()
        ["allowed"]
    )

    print(
        "Normal execution allowed: PASS"
    )

    print(
        "Emergency shutdown blocks execution: PASS"
    )

    print(
        "Kill switch recovery: PASS"
    )

    # ---------------------------------------------------------
    # BROKER HEALTH
    # ---------------------------------------------------------

    print()
    print("6. BROKER HEALTH")
    print("-" * 60)

    health = Phase21BrokerHealth()

    health_result = health.check(
        broker
    )

    assert health_result["healthy"]

    print(
        "Broker health check: PASS"
    )

    # ---------------------------------------------------------
    # POSITION RECONCILIATION
    # ---------------------------------------------------------

    print()
    print("7. POSITION RECONCILIATION")
    print("-" * 60)

    reconciler = (
        Phase21PositionReconciler()
    )

    reconciliation = (
        reconciler.reconcile(
            broker_positions=(
                broker.get_positions()
            ),
            expected_positions={},
        )
    )

    assert reconciliation[
        "reconciled"
    ]

    print(
        "Position reconciliation: PASS"
    )

    # ---------------------------------------------------------
    # EXECUTION GATE
    # ---------------------------------------------------------

    print()
    print("8. EXECUTION GATE")
    print("-" * 60)

    gate = Phase21ExecutionGate(
        config=phase21_config,
        order_validator=validator,
        idempotency_guard=(
            Phase21IdempotencyGuard()
        ),
        kill_switch=(
            Phase21KillSwitch(
                enabled=True,
                active=False,
            )
        ),
        broker_health=health,
    )

    authorization = gate.authorize(
        broker=broker,
        symbol="NIFTY",
        quantity=1,
        price=100.0,
        side="BUY",
        idempotency_key=(
            "PHASE21-TEST-001"
        ),
    )

    assert authorization[
        "authorized"
    ]

    print(
        "Execution gate certification: PASS"
    )

    # ---------------------------------------------------------
    # AUDIT
    # ---------------------------------------------------------

    print()
    print("9. AUDIT LOGGING")
    print("-" * 60)

    audit = Phase21ExecutionAudit(
        directory=(
            phase21_config.REPORT_DIRECTORY
        ),
        filename=(
            phase21_config.AUDIT_FILENAME
        ),
    )

    audit.record(
        "INTEGRATION_TEST",
        {
            "status": "PASS",
        },
    )

    assert (
        len(audit.events())
        > 0
    )

    print(
        "Execution audit logging: PASS"
    )

    # ---------------------------------------------------------
    # CERTIFICATION WORKER
    # ---------------------------------------------------------

    print()
    print("10. PHASE 21 CERTIFICATION")
    print("-" * 60)

    worker = Phase21CertificationWorker(
        config=phase21_config,
        execution_gate=gate,
        reconciler=reconciler,
        audit=audit,
        kill_switch=kill_switch,
        report_directory=(
            phase21_config.REPORT_DIRECTORY
        ),
        report_filename=(
            phase21_config.REPORT_FILENAME
        ),
    )

    result = worker.run(
        broker=broker
    )

    assert result["certified"]

    print(
        "Execution certification: PASS"
    )

    print(
        "Real orders placed:",
        result["real_orders_placed"],
    )

    assert (
        result["real_orders_placed"]
        == 0
    )

    # ---------------------------------------------------------
    # JSON REPORT
    # ---------------------------------------------------------

    print()
    print("11. JSON REPORT")
    print("-" * 60)

    report_path = (
        Path(
            phase21_config.REPORT_DIRECTORY
        )
        / phase21_config.REPORT_FILENAME
    )

    assert report_path.exists()

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        report = json.load(file)

    assert report["certified"]

    print(
        f"Report: {report_path} PASS"
    )

    # ---------------------------------------------------------
    # FINAL SAFETY
    # ---------------------------------------------------------

    print()
    print("12. SAFETY")
    print("-" * 60)

    assert (
        phase21_config.ALLOW_LIVE_TRADING
        is False
    )

    assert (
        phase21_config.ALLOW_REAL_BROKER_ORDERS
        is False
    )

    assert (
        phase21_config.LIVE_BROKER_ENABLED
        is False
    )

    assert (
        result["real_orders_placed"]
        == 0
    )

    print(
        "Live trading disabled: PASS"
    )

    print(
        "Real broker disabled: PASS"
    )

    print(
        "No real broker orders: PASS"
    )

    # ---------------------------------------------------------
    # FINAL VALIDATION
    # ---------------------------------------------------------

    print()
    print("13. FINAL VALIDATION")
    print("-" * 60)

    checks = [
        (
            "Paper broker",
            broker.is_connected(),
        ),
        (
            "Paper mode",
            phase21_config.RUNTIME_MODE
            == "PAPER",
        ),
        (
            "Live trading disabled",
            phase21_config.ALLOW_LIVE_TRADING
            is False,
        ),
        (
            "Real broker disabled",
            phase21_config.ALLOW_REAL_BROKER_ORDERS
            is False,
        ),
        (
            "Live broker disabled",
            phase21_config.LIVE_BROKER_ENABLED
            is False,
        ),
        (
            "Order validation",
            valid_order["passed"],
        ),
        (
            "Duplicate protection",
            duplicate["duplicate"],
        ),
        (
            "Kill switch",
            blocked["allowed"]
            is False,
        ),
        (
            "Broker health",
            health_result["healthy"],
        ),
        (
            "Position reconciliation",
            reconciliation["reconciled"],
        ),
        (
            "Execution gate",
            authorization["authorized"],
        ),
        (
            "Execution certification",
            result["certified"],
        ),
        (
            "Real orders untouched",
            result["real_orders_placed"]
            == 0,
        ),
    ]

    for name, passed in checks:

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

        assert passed

    print()
    print("=" * 60)

    print(
        "PHASE 21 INTEGRATION TEST PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

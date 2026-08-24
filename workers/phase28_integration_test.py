import json
from pathlib import Path

from config import phase28_config

from workers.observability.phase28_observability_worker import (
    Phase28ObservabilityWorker,
)


def line():
    print("-" * 60)


def result(label, passed):
    print(
        f"{label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )


def main():

    print("=" * 60)
    print(
        "PHASE 28 PRODUCTION OBSERVABILITY / "
        "INCIDENT RECOVERY INTEGRATION TEST"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # CONFIGURATION
    # --------------------------------------------------------

    print()
    print("1. CONFIGURATION")
    line()

    config_safe = (
        phase28_config.PHASE28_ENABLED
        and phase28_config.LIVE_TRADING_ENABLED is False
        and phase28_config.REAL_BROKER_ENABLED is False
        and phase28_config.PLACE_REAL_ORDERS is False
    )

    result(
        "Phase 28 configuration: ",
        config_safe,
    )

    # --------------------------------------------------------
    # WORKER
    # --------------------------------------------------------

    print()
    print("2. OBSERVABILITY WORKER")
    line()

    worker = Phase28ObservabilityWorker()

    result(
        "Worker initialization: ",
        worker is not None,
    )

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    print()
    print("3. SAFETY")
    line()

    safety = worker.safety.validate()

    result(
        "Live trading disabled: ",
        safety["live_trading_enabled"] is False,
    )

    result(
        "Real broker disabled: ",
        safety["real_broker_enabled"] is False,
    )

    result(
        "Real orders disabled: ",
        safety["place_real_orders"] is False,
    )

    result(
        "Execution safety: ",
        safety["safe"] is True,
    )

    # --------------------------------------------------------
    # HEALTH MONITORING
    # --------------------------------------------------------

    print()
    print("4. HEALTH MONITORING")
    line()

    components = (
        worker.health.REQUIRED_COMPONENTS
    )

    for component in components:
        worker.observe_component(
            component=component,
            healthy=True,
        )

    health = worker.health.snapshot()

    result(
        "Required components: ",
        health["required_count"]
        >= phase28_config.MIN_COMPONENTS,
    )

    result(
        "Healthy components: ",
        health["healthy_count"]
        >= phase28_config.MIN_HEALTHY_COMPONENTS,
    )

    result(
        "All components healthy: ",
        health["all_required_healthy"] is True,
    )

    # --------------------------------------------------------
    # INCIDENT DETECTION
    # --------------------------------------------------------

    print()
    print("5. INCIDENT DETECTION")
    line()

    before = len(
        worker.incidents.incidents
    )

    worker.observe_component(
        component="test_component",
        healthy=False,
        details={
            "test": True,
        },
        auto_recover=True,
    )

    after = len(
        worker.incidents.incidents
    )

    result(
        "Incident detection: ",
        after == before + 1,
    )

    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    print()
    print("6. AUTOMATIC RECOVERY")
    line()

    recovery = (
        worker.recovery.snapshot()
    )

    result(
        "Recovery attempted: ",
        recovery["recovery_attempts"] >= 1,
    )

    result(
        "Recovery successful: ",
        recovery["successful_recoveries"] >= 1,
    )

    # --------------------------------------------------------
    # SAFETY INCIDENT
    # --------------------------------------------------------

    print()
    print("7. SAFETY INCIDENT PROTECTION")
    line()

    unsafe_worker = Phase28ObservabilityWorker()

    unsafe_worker.safety.live_trading_enabled = True

    unsafe_state = (
        unsafe_worker.safety.validate()
    )

    result(
        "Unsafe configuration detected: ",
        unsafe_state["safe"] is False,
    )

    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

    print()
    print("8. READINESS")
    line()

    # Use a clean worker for the final readiness result.
    clean_worker = Phase28ObservabilityWorker()

    report = clean_worker.run(
        phase27_ready=True
    )

    readiness = report["readiness"]

    result(
        "Observability readiness: ",
        readiness["ready"] is True,
    )

    print(
        "Classification:",
        readiness["classification"],
    )

    print(
        "Readiness score:",
        readiness["score"],
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()
    print("9. JSON REPORT")
    line()

    report_path = Path(
        report["report_path"]
    )

    result(
        "Report exists: ",
        report_path.exists(),
    )

    valid_json = False

    if report_path.exists():

        try:

            with report_path.open(
                "r",
                encoding="utf-8",
            ) as handle:

                json.load(handle)

            valid_json = True

        except Exception:
            valid_json = False

    result(
        "Report valid JSON: ",
        valid_json,
    )

    # --------------------------------------------------------
    # AUDIT
    # --------------------------------------------------------

    print()
    print("10. AUDIT LOGGING")
    line()

    audit_path = Path(
        phase28_config.REPORT_DIRECTORY
    ) / phase28_config.AUDIT_FILENAME

    result(
        "Audit log exists: ",
        audit_path.exists(),
    )

    # --------------------------------------------------------
    # FINAL SAFETY
    # --------------------------------------------------------

    print()
    print("11. FINAL SAFETY")
    line()

    final_safety = (
        report["safety"]
    )

    result(
        "No real broker orders: ",
        report["real_orders_placed"] == 0,
    )

    result(
        "Live trading disabled: ",
        report["live_trading_enabled"] is False,
    )

    result(
        "Real broker disabled: ",
        report["real_broker_enabled"] is False,
    )

    result(
        "Real order placement disabled: ",
        report["place_real_orders"] is False,
    )

    result(
        "Safety gate passed: ",
        final_safety["safe"] is True,
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    all_passed = (
        config_safe
        and readiness["ready"]
        and report["real_orders_placed"] == 0
        and report["live_trading_enabled"] is False
        and report["real_broker_enabled"] is False
        and report["place_real_orders"] is False
        and final_safety["safe"] is True
        and report_path.exists()
        and valid_json
        and audit_path.exists()
    )

    print()
    print("=" * 60)

    if all_passed:

        print(
            "PHASE 28 INTEGRATION TEST PASSED"
        )

    else:

        print(
            "PHASE 28 INTEGRATION TEST FAILED"
        )

        raise SystemExit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()

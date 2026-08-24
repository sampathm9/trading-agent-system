import json
from pathlib import Path

from config import phase27_config

from workers.runtime.phase27_runtime_worker import (
    Phase27RuntimeWorker,
)


def check(label, condition):

    status = "PASS" if condition else "FAIL"

    print(
        f"{label}: {status}"
    )

    if not condition:
        raise AssertionError(
            f"{label} failed"
        )


def main():

    print("=" * 60)
    print(
        "PHASE 27 PRODUCTION RUNTIME "
        "ORCHESTRATION INTEGRATION TEST"
    )
    print("=" * 60)

    worker = (
        Phase27RuntimeWorker()
    )

    # --------------------------------------------------------
    # 1. CONFIGURATION
    # --------------------------------------------------------

    print()
    print("1. CONFIGURATION")
    print("-" * 60)

    check(
        "Phase 27 enabled",
        phase27_config.PHASE27_ENABLED
        is True,
    )

    check(
        "Shadow mode enabled",
        phase27_config.SHADOW_MODE
        is True,
    )

    check(
        "Live trading disabled",
        phase27_config.LIVE_TRADING_ENABLED
        is False,
    )

    check(
        "Real broker disabled",
        phase27_config.REAL_BROKER_ENABLED
        is False,
    )

    check(
        "Real orders disabled",
        phase27_config.PLACE_REAL_ORDERS
        is False,
    )

    check(
        "Runtime activation disabled",
        phase27_config.RUNTIME_ACTIVATION_ENABLED
        is False,
    )

    # --------------------------------------------------------
    # 2. COMPONENT REGISTRATION
    # --------------------------------------------------------

    print()
    print("2. COMPONENT REGISTRATION")
    print("-" * 60)

    components = (
        worker.register_required_components()
    )

    check(
        "Required components registered",
        len(components)
        == len(
            phase27_config.REQUIRED_COMPONENTS
        ),
    )

    check(
        "All components healthy",
        worker.registry.all_healthy(),
    )

    # --------------------------------------------------------
    # 3. PREFLIGHT
    # --------------------------------------------------------

    print()
    print("3. PREFLIGHT")
    print("-" * 60)

    preflight = (
        worker.run_preflight()
    )

    check(
        "Preflight validation",
        preflight["passed"],
    )

    check(
        "Safety validation",
        preflight["safety"]["safe"],
    )

    check(
        "Component health",
        preflight["components_healthy"],
    )

    # --------------------------------------------------------
    # 4. RUNTIME START
    # --------------------------------------------------------

    print()
    print("4. RUNTIME START")
    print("-" * 60)

    started = worker.start()

    check(
        "Runtime start",
        started["started"],
    )

    check(
        "Runtime running",
        worker.state_machine.is_running(),
    )

    # --------------------------------------------------------
    # 5. CANDLE PROCESSING
    # --------------------------------------------------------

    print()
    print("5. RUNTIME PROCESSING")
    print("-" * 60)

    processed = 0

    for _ in range(10):

        if worker.process_candle():
            processed += 1

    check(
        "Runtime candle processing",
        processed == 10,
    )

    check(
        "Runtime processed candles",
        worker.session.candles_processed
        == 10,
    )

    # --------------------------------------------------------
    # 6. HEALTH
    # --------------------------------------------------------

    print()
    print("6. HEALTH MONITORING")
    print("-" * 60)

    health = worker.health.check()

    check(
        "Runtime health",
        health["healthy"],
    )

    # --------------------------------------------------------
    # 7. EMERGENCY SHUTDOWN
    # --------------------------------------------------------

    print()
    print("7. EMERGENCY SHUTDOWN")
    print("-" * 60)

    worker.emergency_shutdown()

    check(
        "Emergency stop state",
        worker.state_machine.state.value
        == "EMERGENCY_STOP",
    )

    check(
        "Emergency safety active",
        worker.safety.emergency_stop
        is True,
    )

    check(
        "Processing blocked",
        worker.process_candle()
        is False,
    )

    # --------------------------------------------------------
    # 8. RECOVERY
    # --------------------------------------------------------

    print()
    print("8. RECOVERY")
    print("-" * 60)

    worker.recover()

    check(
        "Emergency recovery",
        worker.safety.emergency_stop
        is False,
    )

    check(
        "Runtime ready after recovery",
        worker.state_machine.state.value
        == "READY",
    )

    # --------------------------------------------------------
    # 9. RESTART
    # --------------------------------------------------------

    print()
    print("9. CONTROLLED RESTART")
    print("-" * 60)

    restarted = worker.start()

    check(
        "Runtime restart",
        restarted["started"],
    )

    check(
        "Runtime running after recovery",
        worker.state_machine.is_running(),
    )

    # --------------------------------------------------------
    # 10. NORMAL STOP
    # --------------------------------------------------------

    print()
    print("10. CONTROLLED STOP")
    print("-" * 60)

    stopped = worker.stop()

    check(
        "Runtime stop",
        stopped,
    )

    check(
        "Runtime stopped",
        worker.state_machine.state.value
        == "STOPPED",
    )

    # --------------------------------------------------------
    # 11. REPORT
    # --------------------------------------------------------

    print()
    print("11. JSON REPORT")
    print("-" * 60)

    report_path, report = (
        worker.write_report()
    )

    check(
        "Report generated",
        report_path.exists(),
    )

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as handle:

        loaded = json.load(handle)

    check(
        "Report valid JSON",
        isinstance(loaded, dict),
    )

    check(
        "Readiness classification",
        loaded["readiness"]["classification"]
        == "PAPER_RUNTIME_READY",
    )

    # --------------------------------------------------------
    # 12. SAFETY
    # --------------------------------------------------------

    print()
    print("12. FINAL SAFETY")
    print("-" * 60)

    check(
        "No real broker used",
        loaded["real_broker_used"]
        is False,
    )

    check(
        "Real orders placed",
        loaded["real_orders_placed"]
        == 0,
    )

    check(
        "Live trading disabled",
        loaded["live_trading_enabled"]
        is False,
    )

    check(
        "Shadow mode",
        phase27_config.SHADOW_MODE
        is True,
    )

    print()
    print("=" * 60)
    print(
        "PHASE 27 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

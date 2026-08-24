import json
from pathlib import Path

from config import phase30_config

from workers.release_control.release_safety import (
    ReleaseSafetyController,
)
from workers.release_control.phase_report_verifier import (
    PhaseReportVerifier,
)
from workers.release_control.release_gate import (
    FinalReleaseGate,
)
from workers.release_control.release_readiness import (
    ReleaseReadiness,
)
from workers.release_control.phase30_release_worker import (
    Phase30ReleaseWorker,
)


def section(number, title):
    print()
    print(f"{number}. {title}")
    print("-" * 60)


def result(label, passed):

    print(
        f"{label}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    return bool(passed)


def main():

    print("=" * 60)
    print(
        "PHASE 30 PRODUCTION SESSION CONTROL "
        "AND FINAL RELEASE CERTIFICATION"
    )
    print("=" * 60)

    all_passed = True

    # --------------------------------------------------------
    # CONFIGURATION
    # --------------------------------------------------------

    section(1, "CONFIGURATION")

    config_ok = (
        phase30_config.PHASE30_ENABLED
        and phase30_config.PAPER_MODE
        and phase30_config.SHADOW_MODE
        and not phase30_config.LIVE_TRADING_ENABLED
        and not phase30_config.REAL_BROKER_ENABLED
        and not phase30_config.PLACE_REAL_ORDERS
    )

    all_passed &= result(
        "Phase 30 configuration",
        config_ok,
    )

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    section(2, "SAFETY")

    safety = ReleaseSafetyController(
        phase30_config
    )

    safety_result = safety.validate()

    all_passed &= result(
        "Paper mode",
        safety_result["checks"]["paper_mode"],
    )

    all_passed &= result(
        "Shadow mode",
        safety_result["checks"]["shadow_mode"],
    )

    all_passed &= result(
        "Live trading disabled",
        safety_result["checks"][
            "live_trading_disabled"
        ],
    )

    all_passed &= result(
        "Real broker disabled",
        safety_result["checks"][
            "real_broker_disabled"
        ],
    )

    all_passed &= result(
        "Real orders disabled",
        safety_result["checks"][
            "real_orders_disabled"
        ],
    )

    # --------------------------------------------------------
    # PHASE REPORTS
    # --------------------------------------------------------

    section(3, "PREVIOUS PHASE VERIFICATION")

    verifier = PhaseReportVerifier(".")

    phase_result = verifier.verify_required_phases()

    all_passed &= result(
        "Required Phase 23-29 reports",
        phase_result["passed"],
    )

    for phase, item in phase_result[
        "reports"
    ].items():

        all_passed &= result(
            f"Phase {phase} report",
            item["exists"]
            and item["valid"],
        )

    # --------------------------------------------------------
    # RELEASE GATE
    # --------------------------------------------------------

    section(4, "FINAL RELEASE GATE")

    gate = FinalReleaseGate(
        phase30_config,
        safety,
        verifier,
    )

    gate_result = gate.evaluate()

    all_passed &= result(
        "Release gate",
        gate_result["ready"],
    )

    print(
        "Release classification:",
        gate_result["classification"],
    )

    print(
        "Release score:",
        gate_result["score"],
    )

    # --------------------------------------------------------
    # SESSION CONTROL
    # --------------------------------------------------------

    section(5, "PRODUCTION SESSION CONTROL")

    from workers.release_control.session_controller import (
        ProductionSessionController,
    )

    session = ProductionSessionController(
        phase30_config,
        safety,
    )

    start_result = session.start()

    all_passed &= result(
        "Paper session start",
        start_result["started"],
    )

    trade_gate = session.can_trade()

    all_passed &= result(
        "Session trade gate",
        trade_gate["allowed"],
    )

    session.register_trade(10.0)

    all_passed &= result(
        "Trade accounting",
        session.trade_count == 1,
    )

    session.stop()

    # --------------------------------------------------------
    # EMERGENCY STOP
    # --------------------------------------------------------

    section(6, "EMERGENCY STOP")

    safety.activate_emergency_stop()

    blocked = not safety.execution_allowed()

    all_passed &= result(
        "Emergency stop blocks execution",
        blocked,
    )

    safety.recover_emergency_stop()

    recovered = safety.execution_allowed()

    all_passed &= result(
        "Emergency stop recovery",
        recovered,
    )

    # --------------------------------------------------------
    # FULL WORKER
    # --------------------------------------------------------

    section(7, "FULL RELEASE WORKER")

    worker = Phase30ReleaseWorker(
        phase30_config,
        ".",
    )

    report = worker.run()

    readiness = report["readiness"]

    all_passed &= result(
        "Release worker",
        readiness["ready"],
    )

    print(
        "Readiness classification:",
        readiness["classification"],
    )

    print(
        "Readiness score:",
        readiness["score"],
    )

    # --------------------------------------------------------
    # JSON REPORT
    # --------------------------------------------------------

    section(8, "JSON REPORT")

    report_path = (
        Path(
            phase30_config.REPORT_DIRECTORY
        )
        / phase30_config.REPORT_FILENAME
    )

    report_exists = report_path.exists()

    all_passed &= result(
        "Report exists",
        report_exists,
    )

    valid_json = False

    if report_exists:

        try:

            with report_path.open(
                "r",
                encoding="utf-8",
            ) as handle:

                data = json.load(handle)

            valid_json = (
                isinstance(data, dict)
                and data.get("phase") == 30
            )

        except Exception:
            valid_json = False

    all_passed &= result(
        "Report valid JSON",
        valid_json,
    )

    # --------------------------------------------------------
    # FINAL SAFETY
    # --------------------------------------------------------

    section(9, "FINAL SAFETY")

    all_passed &= result(
        "No real broker orders",
        report.get(
            "real_orders_placed",
            -1,
        ) == 0,
    )

    all_passed &= result(
        "Live trading disabled",
        report.get(
            "live_trading_enabled"
        ) is False,
    )

    all_passed &= result(
        "Real broker disabled",
        report.get(
            "real_broker_enabled"
        ) is False,
    )

    all_passed &= result(
        "Real order placement disabled",
        report.get(
            "place_real_orders"
        ) is False,
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 60)

    if all_passed:

        print(
            "PHASE 30 INTEGRATION TEST PASSED"
        )

    else:

        print(
            "PHASE 30 INTEGRATION TEST FAILED"
        )

    print("=" * 60)

    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

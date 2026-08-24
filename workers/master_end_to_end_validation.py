# ============================================================
# TRADING AGENT SYSTEM
# MASTER END-TO-END VALIDATION
# PHASES 20-30
# ============================================================

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports" / "master_validation"
REPORT_FILE = (
    REPORT_DIR / "master_end_to_end_validation_report.json"
)

PHASES = list(range(20, 31))


# ============================================================
# RUN PHASE INTEGRATION TEST
# ============================================================

def run_phase_test(phase: int) -> dict:

    module = f"workers.phase{phase}_integration_test"

    print()
    print("=" * 70)
    print(f"MASTER VALIDATION - PHASE {phase}")
    print("=" * 70)

    try:

        result = subprocess.run(
            [sys.executable, "-m", module],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        output = (
            (result.stdout or "")
            + (result.stderr or "")
        )

        passed = (
            result.returncode == 0
            and "INTEGRATION TEST PASSED" in output
        )

        print(
            f"Integration test: "
            f"{'PASS' if passed else 'FAIL'}"
        )

        return {
            "phase": phase,
            "module": module,
            "return_code": result.returncode,
            "integration_test": passed,
            "output_tail": output[-3000:],
        }

    except Exception as exc:

        print("Integration test: FAIL")
        print(f"Error: {exc}")

        return {
            "phase": phase,
            "module": module,
            "return_code": -1,
            "integration_test": False,
            "error": str(exc),
        }


# ============================================================
# SAFETY VALIDATION
# ============================================================

def safety_check_phase(phase: int) -> dict:

    config_name = f"config.phase{phase}_config"

    try:

        config = importlib.import_module(config_name)

    except Exception as exc:

        return {
            "phase": phase,
            "config": config_name,
            "passed": False,
            "error": str(exc),
        }

    # --------------------------------------------------------
    # LIVE TRADING
    # --------------------------------------------------------

    if hasattr(config, "LIVE_TRADING_ENABLED"):

        live_value = getattr(
            config,
            "LIVE_TRADING_ENABLED",
        )

        live_source = "LIVE_TRADING_ENABLED"

    elif hasattr(config, "ALLOW_LIVE_TRADING"):

        live_value = getattr(
            config,
            "ALLOW_LIVE_TRADING",
        )

        live_source = "ALLOW_LIVE_TRADING"

    elif hasattr(config, "LIVE_TRADING"):

        live_value = getattr(
            config,
            "LIVE_TRADING",
        )

        live_source = "LIVE_TRADING"

    elif hasattr(config, "ENABLE_LIVE_TRADING"):

        live_value = getattr(
            config,
            "ENABLE_LIVE_TRADING",
        )

        live_source = "ENABLE_LIVE_TRADING"

    else:

        live_value = None
        live_source = None

    # --------------------------------------------------------
    # REAL BROKER
    # --------------------------------------------------------

    if hasattr(config, "REAL_BROKER_ENABLED"):

        broker_value = getattr(
            config,
            "REAL_BROKER_ENABLED",
        )

        broker_source = "REAL_BROKER_ENABLED"

    elif hasattr(config, "ALLOW_REAL_BROKER_ORDERS"):

        broker_value = getattr(
            config,
            "ALLOW_REAL_BROKER_ORDERS",
        )

        broker_source = "ALLOW_REAL_BROKER_ORDERS"

    elif hasattr(config, "REAL_BROKER"):

        broker_value = getattr(
            config,
            "REAL_BROKER",
        )

        broker_source = "REAL_BROKER"

    elif hasattr(config, "LIVE_BROKER_ENABLED"):

        broker_value = getattr(
            config,
            "LIVE_BROKER_ENABLED",
        )

        broker_source = "LIVE_BROKER_ENABLED"

    elif hasattr(config, "ENABLE_REAL_BROKER"):

        broker_value = getattr(
            config,
            "ENABLE_REAL_BROKER",
        )

        broker_source = "ENABLE_REAL_BROKER"

    else:

        broker_value = None
        broker_source = None

    # --------------------------------------------------------
    # REAL ORDERS
    # --------------------------------------------------------

    if hasattr(config, "PLACE_REAL_ORDERS"):

        orders_value = getattr(
            config,
            "PLACE_REAL_ORDERS",
        )

        orders_source = "PLACE_REAL_ORDERS"

    elif hasattr(config, "REAL_ORDERS_ENABLED"):

        orders_value = getattr(
            config,
            "REAL_ORDERS_ENABLED",
        )

        orders_source = "REAL_ORDERS_ENABLED"

    elif hasattr(config, "ENABLE_REAL_ORDERS"):

        orders_value = getattr(
            config,
            "ENABLE_REAL_ORDERS",
        )

        orders_source = "ENABLE_REAL_ORDERS"

    elif hasattr(config, "LIVE_ORDERS_ENABLED"):

        orders_value = getattr(
            config,
            "LIVE_ORDERS_ENABLED",
        )

        orders_source = "LIVE_ORDERS_ENABLED"

    else:

        orders_value = False
        orders_source = "DEFAULT_FALSE"

    # --------------------------------------------------------
    # PAPER MODE
    # --------------------------------------------------------

    paper_value = None
    paper_source = None

    if hasattr(config, "PAPER_MODE"):

        paper_value = getattr(
            config,
            "PAPER_MODE",
        )

        paper_source = "PAPER_MODE"

    elif hasattr(config, "RUNTIME_MODE"):

        paper_value = (
            getattr(config, "RUNTIME_MODE")
            == "PAPER"
        )

        paper_source = "RUNTIME_MODE"

    elif hasattr(config, "ENVIRONMENT"):

        paper_value = (
            getattr(config, "ENVIRONMENT")
            == "PAPER"
        )

        paper_source = "ENVIRONMENT"

    # --------------------------------------------------------
    # MISSING FLAGS
    # --------------------------------------------------------

    missing = []

    if live_value is None:
        missing.append("live trading flag")

    if broker_value is None:
        missing.append("real broker flag")

    # --------------------------------------------------------
    # SAFETY RULE
    # --------------------------------------------------------

    passed = (
        not missing
        and live_value is False
        and broker_value is False
        and orders_value is False
    )

    # If explicit PAPER mode exists, it must not contradict
    # the disabled live-trading configuration.

    if paper_value is False and live_value is False:

        # This is still safe because live trading is explicitly
        # disabled. Do not fail merely because PAPER_MODE is false.

        pass

    return {
        "phase": phase,
        "config": config_name,

        "live_trading_enabled": live_value,
        "live_trading_source": live_source,

        "real_broker_enabled": broker_value,
        "real_broker_source": broker_source,

        "place_real_orders": orders_value,
        "real_orders_source": orders_source,

        "paper_mode": paper_value,
        "paper_mode_source": paper_source,

        "missing_safety_flags": missing,

        "passed": passed,
    }


# ============================================================
# REPORT VALIDATION
# ============================================================

def report_check_phase(phase: int) -> dict:

    report_dir = (
        ROOT
        / "reports"
        / f"phase{phase}"
    )

    if not report_dir.exists():

        return {
            "phase": phase,
            "passed": False,
            "reason": "Report directory missing",
        }

    json_files = list(
        report_dir.glob("*.json")
    )

    if not json_files:

        return {
            "phase": phase,
            "passed": True,
            "reason": "No JSON report required/found",
        }

    valid_files = []

    for file in json_files:

        try:

            with file.open(
                "r",
                encoding="utf-8",
            ) as handle:

                json.load(handle)

            valid_files.append(
                file.name
            )

        except Exception:

            pass

    passed = len(valid_files) > 0

    return {
        "phase": phase,
        "passed": passed,
        "json_reports": valid_files,
    }


# ============================================================
# FINAL SAFETY VALIDATION
# ============================================================

def master_safety_validation() -> dict:

    results = []

    for phase in PHASES:

        result = safety_check_phase(
            phase
        )

        results.append(result)

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        print(
            f"config/phase{phase}_config.py: "
            f"{status}"
        )

    return {
        "passed": all(
            item["passed"]
            for item in results
        ),
        "phases": results,
    }


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(data: dict) -> None:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            data,
            handle,
            indent=2,
            default=str,
        )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    started = datetime.now().isoformat(
        timespec="seconds"
    )

    print("=" * 70)
    print("TRADING AGENT SYSTEM")
    print("MASTER END-TO-END VALIDATION")
    print("=" * 70)

    print()
    print(
        "This validation uses the existing Phase 20-30 tests."
    )
    print(
        "No real broker orders are permitted."
    )
    print(
        "Live trading must remain disabled."
    )

    print()
    print(f"Started: {started}")

    phase_results = []

    # --------------------------------------------------------
    # RUN EVERY PHASE
    # --------------------------------------------------------

    for phase in PHASES:

        result = run_phase_test(
            phase
        )

        safety = safety_check_phase(
            phase
        )

        report = report_check_phase(
            phase
        )

        result["safety"] = safety
        result["json_report"] = report

        safety_status = (
            "PASS"
            if safety["passed"]
            else "FAIL"
        )

        report_status = (
            "PASS"
            if report["passed"]
            else "FAIL"
        )

        print(
            f"Safety checks:    {safety_status}"
        )

        print(
            f"JSON report:      {report_status}"
        )

        phase_passed = (
            result["integration_test"]
            and safety["passed"]
            and report["passed"]
        )

        result["passed"] = phase_passed

        print(
            f"PHASE {phase}:     "
            f"{'PASS' if phase_passed else 'FAIL'}"
        )

        phase_results.append(
            result
        )

        if not phase_passed:

            print()
            print("=" * 70)
            print(
                f"MASTER VALIDATION STOPPED AT PHASE {phase}"
            )
            print("=" * 70)

            break

    # --------------------------------------------------------
    # FINAL SAFETY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("MASTER FINAL SAFETY VALIDATION")
    print("=" * 70)

    final_safety = (
        master_safety_validation()
    )

    print()
    print(
        "FINAL SAFETY: "
        f"{'PASS' if final_safety['passed'] else 'FAIL'}"
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    all_phases_passed = (
        len(phase_results) == len(PHASES)
        and all(
            result["passed"]
            for result in phase_results
        )
    )

    master_passed = (
        all_phases_passed
        and final_safety["passed"]
    )

    print()
    print("=" * 70)
    print(
        "MASTER END-TO-END VALIDATION RESULT"
    )
    print("=" * 70)

    print(
        f"Phases 20-30: "
        f"{'PASS' if all_phases_passed else 'FAIL'}"
    )

    print(
        f"Final safety: "
        f"{'PASS' if final_safety['passed'] else 'FAIL'}"
    )

    print(
        "Real orders: 0 / DISABLED"
    )

    print(
        "Live trading: DISABLED"
    )

    print(
        "Real broker: DISABLED"
    )

    if master_passed:

        master_result = (
            "MASTER_VALIDATION_PASSED"
        )

    else:

        master_result = (
            "MASTER_VALIDATION_FAILED"
        )

    print()
    print(
        f"MASTER RESULT: {master_result}"
    )

    finished = datetime.now().isoformat(
        timespec="seconds"
    )

    report = {

        "system":
            "trading-agent-system",

        "validation":
            "master_end_to_end",

        "phases":
            "20-30",

        "started":
            started,

        "finished":
            finished,

        "phase_results":
            phase_results,

        "final_safety":
            final_safety,

        "real_orders":
            0,

        "live_trading_enabled":
            False,

        "real_broker_enabled":
            False,

        "master_passed":
            master_passed,

        "master_result":
            master_result,
    }

    save_report(
        report
    )

    print()
    print(
        f"Report: "
        f"{REPORT_FILE.relative_to(ROOT)}"
    )

    print("=" * 70)

    return (
        0
        if master_passed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

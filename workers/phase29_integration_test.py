import json
import os
import sys

import config.phase29_config as phase29_config

from workers.governance.phase29_governance_worker import (
    Phase29GovernanceWorker,
)


def check(name, passed):

    status = "PASS" if passed else "FAIL"

    print(
        f"{name}: {status}"
    )

    return bool(passed)


def main():

    print("=" * 60)
    print(
        "PHASE 29 OPERATIONAL GOVERNANCE & COMPLIANCE "
        "INTEGRATION TEST"
    )
    print("=" * 60)

    print("")
    print("1. CONFIGURATION")
    print("-" * 60)

    config_pass = check(
        "Phase 29 configuration",
        phase29_config.PHASE29_ENABLED is True,
    )

    print("")
    print("2. CONFIGURATION GOVERNANCE")
    print("-" * 60)

    worker = Phase29GovernanceWorker(
        phase29_config
    )

    config_result = (
        worker.configuration.validate(
            phase29_config
        )
    )

    config_governance_pass = check(
        "Configuration governance",
        config_result["passed"],
    )

    print("")
    print("3. DEPLOYMENT VERIFICATION")
    print("-" * 60)

    deployment_result = (
        worker.deployment.verify()
    )

    deployment_pass = check(
        "Deployment verification",
        deployment_result["passed"],
    )

    print("")
    print("4. SESSION AUTHORIZATION")
    print("-" * 60)

    session_result = worker.session.authorize(
        phase29_config.DEFAULT_SESSION,
        phase29_config.LIVE_TRADING_ENABLED,
    )

    session_pass = check(
        "Paper session authorization",
        session_result["authorized"],
    )

    live_result = worker.session.authorize(
        "LIVE",
        False,
    )

    live_blocked_pass = check(
        "LIVE session blocked",
        live_result["authorized"] is False,
    )

    print("")
    print("5. RISK POLICY")
    print("-" * 60)

    risk_result = worker.risk.validate(
        quantity=1,
        daily_trades=0,
        daily_loss=0.0,
        consecutive_losses=0,
    )

    risk_pass = check(
        "Normal risk policy",
        risk_result["passed"],
    )

    risk_failure = worker.risk.validate(
        quantity=(
            phase29_config.MAX_ORDER_QUANTITY
            + 1
        ),
        daily_trades=0,
        daily_loss=0.0,
        consecutive_losses=0,
    )

    risk_limit_pass = check(
        "Quantity limit enforcement",
        risk_failure["passed"] is False,
    )

    print("")
    print("6. AUDIT INTEGRITY")
    print("-" * 60)

    worker.audit.record(
        "TEST_EVENT",
        {
            "test": True,
        },
    )

    audit_result = worker.audit.verify()

    audit_pass = check(
        "Audit integrity",
        audit_result["passed"],
    )

    print("")
    print("7. CONFIGURATION DRIFT")
    print("-" * 60)

    baseline = {
        "live_trading_enabled": False,
        "real_broker_enabled": False,
        "place_real_orders": False,
        "paper_only": True,
    }

    current = dict(baseline)

    drift_result = worker.drift.compare(
        baseline,
        current,
    )

    drift_pass = check(
        "No configuration drift",
        drift_result["passed"],
    )

    changed = dict(baseline)
    changed["live_trading_enabled"] = True

    drift_failure = worker.drift.compare(
        baseline,
        changed,
    )

    drift_detection_pass = check(
        "Configuration drift detection",
        drift_failure["drift_detected"],
    )

    print("")
    print("8. EMERGENCY STOP")
    print("-" * 60)

    emergency_result = (
        worker.emergency.verify()
    )

    emergency_pass = check(
        "Emergency stop verification",
        emergency_result["passed"],
    )

    print("")
    print("9. FULL GOVERNANCE RUN")
    print("-" * 60)

    report = worker.run()

    governance_pass = check(
        "Governance worker",
        report["readiness"]["ready"],
    )

    score = report["readiness"]["score"]

    print(
        f"Governance readiness score: {score}"
    )

    print(
        "Classification:",
        report["readiness"]["classification"],
    )

    print("")
    print("10. SAFETY")
    print("-" * 60)

    live_disabled = check(
        "Live trading disabled",
        report["safety"][
            "live_trading_enabled"
        ] is False,
    )

    real_broker_disabled = check(
        "Real broker disabled",
        report["safety"][
            "real_broker_enabled"
        ] is False,
    )

    real_orders_disabled = check(
        "Real orders disabled",
        report["safety"][
            "place_real_orders"
        ] is False,
    )

    paper_only = check(
        "Paper-only mode",
        report["safety"]["paper_only"] is True,
    )

    zero_orders = check(
        "Real orders placed: 0",
        report["safety"][
            "real_orders_placed"
        ] == 0,
    )

    print("")
    print("11. JSON REPORT")
    print("-" * 60)

    report_path = os.path.join(
        phase29_config.REPORT_DIRECTORY,
        phase29_config.REPORT_FILENAME,
    )

    report_exists = check(
        "Report exists",
        os.path.exists(report_path),
    )

    valid_json = False

    if report_exists:

        try:

            with open(
                report_path,
                "r",
                encoding="utf-8",
            ) as handle:

                json.load(handle)

            valid_json = True

        except Exception:

            valid_json = False

    check(
        "Report valid JSON",
        valid_json,
    )

    print("")
    print("12. AUDIT LOG")
    print("-" * 60)

    audit_path = os.path.join(
        phase29_config.REPORT_DIRECTORY,
        phase29_config.AUDIT_FILENAME,
    )

    audit_exists = check(
        "Audit log exists",
        os.path.exists(audit_path),
    )

    print("")
    print("13. FINAL VALIDATION")
    print("-" * 60)

    results = [
        config_pass,
        config_governance_pass,
        deployment_pass,
        session_pass,
        live_blocked_pass,
        risk_pass,
        risk_limit_pass,
        audit_pass,
        drift_pass,
        drift_detection_pass,
        emergency_pass,
        governance_pass,
        live_disabled,
        real_broker_disabled,
        real_orders_disabled,
        paper_only,
        zero_orders,
        report_exists,
        valid_json,
        audit_exists,
    ]

    final_pass = all(results)

    check(
        "Configuration",
        config_pass,
    )

    check(
        "Governance",
        config_governance_pass,
    )

    check(
        "Deployment verification",
        deployment_pass,
    )

    check(
        "Session authorization",
        session_pass,
    )

    check(
        "LIVE blocked",
        live_blocked_pass,
    )

    check(
        "Risk policy",
        risk_pass,
    )

    check(
        "Risk limits",
        risk_limit_pass,
    )

    check(
        "Audit integrity",
        audit_pass,
    )

    check(
        "Drift detection",
        drift_detection_pass,
    )

    check(
        "Emergency stop",
        emergency_pass,
    )

    check(
        "Governance readiness",
        governance_pass,
    )

    check(
        "Real broker untouched",
        real_broker_disabled,
    )

    check(
        "Real orders untouched",
        zero_orders,
    )

    print("")
    print("=" * 60)

    if final_pass:

        print(
            "PHASE 29 INTEGRATION TEST PASSED"
        )

    else:

        print(
            "PHASE 29 INTEGRATION TEST FAILED"
        )

        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()

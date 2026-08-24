# ============================================================
# PHASE 28 CONFIGURATION
# ============================================================

PHASE28_ENABLED = True

# CRITICAL SAFETY
LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False

# Observability
HEALTH_CHECK_INTERVAL_SECONDS = 30
MAX_HEARTBEAT_AGE_SECONDS = 120

# Incident thresholds
MAX_CONSECUTIVE_FAILURES = 3
MAX_RECOVERY_ATTEMPTS = 3
MAX_DAILY_INCIDENTS = 10

# Runtime safety
REQUIRE_PHASE27_READY = True
REQUIRE_PAPER_OR_SHADOW_MODE = True

# Recovery
AUTO_RECOVERY_ENABLED = True
AUTO_RECOVERY_MUST_REMAIN_PAPER_ONLY = True

# Reports
REPORT_DIRECTORY = "reports/phase28"
REPORT_FILENAME = "phase28_observability_report.json"
AUDIT_FILENAME = "phase28_observability_audit.log"

# Readiness
MIN_COMPONENTS = 5
MIN_HEALTHY_COMPONENTS = 5
MAX_CRITICAL_INCIDENTS = 0

SAFETY_ASSERTIONS = {
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
    "auto_recovery_must_remain_paper_only": True,
}

# ============================================================
# PHASE 29 - OPERATIONAL GOVERNANCE & COMPLIANCE
# ============================================================

PHASE29_ENABLED = True

# ------------------------------------------------------------
# CRITICAL SAFETY
# ------------------------------------------------------------

LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False
PAPER_ONLY = True

# ------------------------------------------------------------
# GOVERNANCE
# ------------------------------------------------------------

REQUIRE_CONFIGURATION_VALIDATION = True
REQUIRE_DEPLOYMENT_VERIFICATION = True
REQUIRE_SESSION_AUTHORIZATION = True
REQUIRE_RISK_POLICY = True
REQUIRE_AUDIT_INTEGRITY = True
REQUIRE_DRIFT_CHECK = True
REQUIRE_EMERGENCY_STOP_VERIFICATION = True

# ------------------------------------------------------------
# RISK LIMITS
# ------------------------------------------------------------

MAX_ORDER_QUANTITY = 100
MAX_DAILY_TRADES = 100
MAX_DAILY_LOSS = 5000.0
MAX_CONSECUTIVE_LOSSES = 5

# ------------------------------------------------------------
# SESSION
# ------------------------------------------------------------

DEFAULT_SESSION = "PAPER"

ALLOWED_SESSIONS = [
    "PAPER",
    "SHADOW",
    "CANARY",
]

LIVE_SESSION_NAME = "LIVE"

# ------------------------------------------------------------
# GOVERNANCE READINESS
# ------------------------------------------------------------

MIN_READINESS_SCORE = 0.90

# ------------------------------------------------------------
# REPORTS
# ------------------------------------------------------------

REPORT_DIRECTORY = "reports/phase29"
REPORT_FILENAME = "phase29_governance_readiness_report.json"
AUDIT_FILENAME = "phase29_governance_audit.log"

# ------------------------------------------------------------
# SAFETY ASSERTIONS
# ------------------------------------------------------------

SAFETY_ASSERTIONS = {
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
    "paper_only": True,
}

# ============================================================
# PHASE 24 - CONTROLLED LIVE ACTIVATION / CANARY GOVERNANCE
# ============================================================

PHASE24_ENABLED = True

# ============================================================
# CRITICAL SAFETY DEFAULTS
# ============================================================

# Phase 24 MUST NOT activate real trading automatically.
SHADOW_MODE = True

LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False

# Explicit activation requires every safety gate to pass.
REQUIRE_EXPLICIT_ACTIVATION = True
REQUIRE_MANUAL_APPROVAL = True
REQUIRE_BROKER_AUTHORIZATION = True
REQUIRE_POSITION_RECONCILIATION = True
REQUIRE_HEALTHY_RUNTIME = True
REQUIRE_PHASE23_READINESS = True

# ============================================================
# TRADING
# ============================================================

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1
DEFAULT_MIN_AI_CONFIDENCE = 0.60

INITIAL_CAPITAL = 100000.0

# ============================================================
# CANARY LIMITS
# ============================================================

CANARY_MAX_ORDERS = 5
CANARY_MAX_QUANTITY = 1
CANARY_MAX_DAILY_LOSS = 1000.0
CANARY_MAX_CONSECUTIVE_LOSSES = 2
CANARY_MAX_OPEN_POSITIONS = 1

# ============================================================
# RUNTIME
# ============================================================

MIN_SIGNAL_CANDLES = 3
MAX_RUNTIME_ERRORS = 3
HEALTH_CHECK_INTERVAL = 1

# ============================================================
# ROLLBACK
# ============================================================

ROLLBACK_ON_ERROR = True
ROLLBACK_ON_LOSS_LIMIT = True
ROLLBACK_ON_HEALTH_FAILURE = True
ROLLBACK_ON_BROKER_FAILURE = True

# ============================================================
# REPORTS
# ============================================================

REPORT_DIRECTORY = "reports/phase24"

REPORT_FILENAME = (
    "phase24_live_activation_readiness_report.json"
)

AUDIT_FILENAME = (
    "phase24_live_activation_audit.log"
)

# ============================================================
# READINESS
# ============================================================

MIN_REQUIRED_SCORE = 0.90

SAFETY_ASSERTIONS = {
    "shadow_mode": True,
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
}

# ============================================================
# PHASE 23 DEPENDENCY
# ============================================================

PHASE23_REPORT = (
    "reports/phase23/phase23_shadow_observation_report.json"
)

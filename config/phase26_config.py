# ============================================================
# PHASE 26 - CANARY PERFORMANCE VALIDATION & AUTOMATIC ROLLBACK
# ============================================================

PHASE26_ENABLED = True

# ------------------------------------------------------------
# CRITICAL SAFETY
# ------------------------------------------------------------

CANARY_MODE = True
LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False

# Automatic rollback is allowed.
# Automatic live activation is NOT allowed.
AUTO_ROLLBACK_ENABLED = True
AUTO_LIVE_ACTIVATION_ENABLED = False

# ------------------------------------------------------------
# SYMBOL / CAPITAL
# ------------------------------------------------------------

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1
INITIAL_CAPITAL = 100000.0

# ------------------------------------------------------------
# CANARY LIMITS
# ------------------------------------------------------------

MAX_CANARY_TRADES = 20
MAX_CONSECUTIVE_LOSSES = 3

MAX_DAILY_LOSS = 1000.0
MAX_DRAWDOWN = 1500.0

MIN_PROFITABLE_TRADE_RATE = 0.40
MIN_EXPECTANCY = 0.0

MAX_REJECTED_ORDERS = 2
MAX_EXECUTION_FAILURES = 1

MAX_HEALTH_FAILURES = 0
MAX_SAFETY_FAILURES = 0

# ------------------------------------------------------------
# VALIDATION REQUIREMENTS
# ------------------------------------------------------------

MIN_CANARY_OBSERVATIONS = 5
MIN_CANARY_TRADES = 1

# ------------------------------------------------------------
# ROLLBACK
# ------------------------------------------------------------

ROLLBACK_ON_RISK_FAILURE = True
ROLLBACK_ON_HEALTH_FAILURE = True
ROLLBACK_ON_EXECUTION_FAILURE = True
ROLLBACK_ON_SAFETY_FAILURE = True
ROLLBACK_ON_PERFORMANCE_FAILURE = True

# ------------------------------------------------------------
# REPORTS
# ------------------------------------------------------------

REPORT_DIRECTORY = "reports/phase26"

REPORT_FILENAME = (
    "phase26_canary_performance_report.json"
)

AUDIT_FILENAME = (
    "phase26_rollback_audit.log"
)

STATE_FILENAME = (
    "phase26_deployment_state.json"
)

# ------------------------------------------------------------
# READINESS
# ------------------------------------------------------------

REQUIRED_PHASE25_REPORT = (
    "reports/phase25/phase25_canary_operation_report.json"
)

MIN_READINESS_SCORE = 0.80

# ------------------------------------------------------------
# SAFETY ASSERTIONS
# ------------------------------------------------------------

SAFETY_ASSERTIONS = {
    "canary_mode": True,
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
    "auto_live_activation_enabled": False,
}

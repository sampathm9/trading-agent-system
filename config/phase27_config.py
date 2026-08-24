# ============================================================
# PHASE 27 - PRODUCTION RUNTIME ORCHESTRATION CONFIGURATION
# ============================================================

PHASE27_ENABLED = True

# ------------------------------------------------------------
# CRITICAL SAFETY
# ------------------------------------------------------------

# Runtime starts in controlled paper/shadow mode.
RUNTIME_MODE = "PAPER"

SHADOW_MODE = True

LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False

# Runtime activation is deliberately disabled by default.
RUNTIME_ACTIVATION_ENABLED = False

# ------------------------------------------------------------
# TRADING
# ------------------------------------------------------------

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1
DEFAULT_MIN_AI_CONFIDENCE = 0.60

# ------------------------------------------------------------
# SESSION
# ------------------------------------------------------------

SESSION_NAME = "PHASE27_PRODUCTION_RUNTIME"

MAX_RUNTIME_CANDLES = 500
MAX_RUNTIME_TRADES = 100
MAX_CONSECUTIVE_LOSSES = 5
MAX_DAILY_LOSS = 5000.0

# ------------------------------------------------------------
# HEALTH
# ------------------------------------------------------------

REQUIRED_COMPONENTS = [
    "historical_data",
    "intelligence",
    "paper_broker",
    "phase17_walk_forward",
    "phase18_robustness",
    "phase19_paper_validation",
    "phase20_production_readiness",
    "phase21_execution_certification",
    "phase22_deployment",
    "phase23_shadow",
    "phase24_activation",
    "phase25_canary",
    "phase26_rollback",
]

# ------------------------------------------------------------
# REPORTS
# ------------------------------------------------------------

REPORT_DIRECTORY = "reports/phase27"

REPORT_FILENAME = (
    "phase27_runtime_orchestration_report.json"
)

AUDIT_FILENAME = (
    "phase27_runtime_audit.log"
)

# ------------------------------------------------------------
# SAFETY ASSERTIONS
# ------------------------------------------------------------

SAFETY_ASSERTIONS = {
    "shadow_mode": True,
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
    "runtime_activation_enabled": False,
}

# ============================================================
# PHASE 30 - PRODUCTION SESSION CONTROL
# ============================================================

PHASE30_ENABLED = True

# CRITICAL SAFETY DEFAULTS
PAPER_MODE = True
SHADOW_MODE = True

LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1
DEFAULT_MIN_AI_CONFIDENCE = 0.60

# Session controls
MAX_SESSION_TRADES = 10
MAX_SESSION_LOSS = 5000.0
MAX_CONSECUTIVE_LOSSES = 3

# Release certification requirements
REQUIRED_PHASE23 = True
REQUIRED_PHASE24 = True
REQUIRED_PHASE25 = True
REQUIRED_PHASE26 = True
REQUIRED_PHASE27 = True
REQUIRED_PHASE28 = True
REQUIRED_PHASE29 = True

MIN_RELEASE_SCORE = 1.0

# Emergency controls
EMERGENCY_STOP_DEFAULT = False
ALLOW_AUTOMATIC_LIVE_ACTIVATION = False
REQUIRE_HUMAN_RELEASE_APPROVAL = True

# Reports
REPORT_DIRECTORY = "reports/phase30"
REPORT_FILENAME = "phase30_release_certification_report.json"
AUDIT_FILENAME = "phase30_release_audit.log"

# Safety assertions
SAFETY_ASSERTIONS = {
    "paper_mode": True,
    "shadow_mode": True,
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
    "automatic_live_activation": False,
    "human_release_approval": True,
}

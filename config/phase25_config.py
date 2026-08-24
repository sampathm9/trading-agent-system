# ============================================================
# PHASE 25 - CONTROLLED CANARY OPERATION & CONTINUOUS MONITORING
# ============================================================

PHASE25_ENABLED = True

# CRITICAL SAFETY
CANARY_MODE = True
PAPER_ONLY = True
SHADOW_MODE = True
LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1
DEFAULT_MIN_AI_CONFIDENCE = 0.60

# Canary limits
MAX_CANARY_TRADES = 10
MAX_CONSECUTIVE_LOSSES = 3
MAX_DAILY_LOSS = 1000.0
MAX_DAILY_PROFIT = 10000.0
MAX_POSITION_QUANTITY = 1

# Monitoring
MIN_HEALTH_SCORE = 0.80
MIN_READINESS_SCORE = 0.80
REQUIRE_BROKER_HEALTH = True
REQUIRE_POSITION_RECONCILIATION = True
REQUIRE_PHASE24_READINESS = True

# Alerts
ALERT_ON_LOSS_LIMIT = True
ALERT_ON_TRADE_LIMIT = True
ALERT_ON_HEALTH_FAILURE = True
ALERT_ON_BROKER_FAILURE = True
ALERT_ON_SAFETY_FAILURE = True

# Reports
REPORT_DIRECTORY = "reports/phase25"
REPORT_FILENAME = "phase25_canary_operation_report.json"
AUDIT_FILENAME = "phase25_canary_audit.log"

SAFETY_ASSERTIONS = {
    "canary_mode": True,
    "paper_only": True,
    "shadow_mode": True,
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
}

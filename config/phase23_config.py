# ============================================================
# PHASE 23 - SHADOW TRADING / LIVE MARKET OBSERVATION
# ============================================================

PHASE23_ENABLED = True

# CRITICAL SAFETY:
# Phase 23 never sends orders to a real broker.
SHADOW_MODE = True
LIVE_TRADING_ENABLED = False
REAL_BROKER_ENABLED = False
PLACE_REAL_ORDERS = False

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1
DEFAULT_MIN_AI_CONFIDENCE = 0.60

# Virtual portfolio
INITIAL_CAPITAL = 100000.0

# Observation controls
MAX_VIRTUAL_TRADES = 100
MAX_CONSECUTIVE_LOSSES = 5
MAX_DAILY_VIRTUAL_LOSS = 5000.0

# Minimum history required before generating a signal
MIN_SIGNAL_CANDLES = 3

# Reports
REPORT_DIRECTORY = "reports/phase23"
REPORT_FILENAME = "phase23_shadow_observation_report.json"
AUDIT_FILENAME = "phase23_shadow_audit.log"

# Readiness
MIN_OBSERVATION_TRADES = 1
MIN_OBSERVATION_CANDLES = 10

# No real broker interaction is permitted.
SAFETY_ASSERTIONS = {
    "shadow_mode": True,
    "live_trading_enabled": False,
    "real_broker_enabled": False,
    "place_real_orders": False,
}

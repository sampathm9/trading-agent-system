# ============================================================
# PHASE 19 CONFIGURATION
# PAPER TRADING / FORWARD VALIDATION
# ============================================================

DEFAULT_SYMBOL = "NIFTY"

INITIAL_CAPITAL = 100000.0

DEFAULT_QUANTITY = 1

MIN_AI_CONFIDENCE = 0.50

MAX_TRADES = 20

MAX_DAILY_LOSS = 5000.0

MAX_CONSECUTIVE_LOSSES = 3

REPORT_DIRECTORY = "reports/phase19"

REPORT_FILENAME = "phase19_paper_trading_report.json"

REQUIRE_PAPER_BROKER = True

ALLOW_REAL_BROKER = False

ENABLE_SAFETY_GATE = True

# Phase 19 remains historical/paper-only.
# No real broker execution is permitted.
PAPER_ONLY = True

"""
Phase 20 production configuration.

Safety-first defaults:
- PAPER mode
- Real broker disabled
- Live orders disabled
"""

RUNTIME_MODE = "PAPER"

ALLOW_LIVE_TRADING = False
ALLOW_REAL_BROKER_ORDERS = False

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1

MAX_QUANTITY = 10
MAX_TRADES_PER_SESSION = 20
MAX_SESSION_LOSS = 5000.0

MIN_AI_CONFIDENCE = 0.50

MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
FORCE_EXIT_TIME = "15:25"

HEARTBEAT_TIMEOUT_SECONDS = 60

REQUIRED_PHASES = [
    17,
    18,
    19,
]

REPORT_DIRECTORY = "reports/phase20"
REPORT_FILENAME = "phase20_production_readiness_report.json"
AUDIT_FILENAME = "phase20_audit.log"

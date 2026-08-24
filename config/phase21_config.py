"""
Phase 21 execution certification configuration.

IMPORTANT:
Phase 21 is paper-only.
Live broker execution is explicitly disabled.
"""

PHASE = 21

RUNTIME_MODE = "PAPER"

ALLOW_LIVE_TRADING = False
ALLOW_REAL_BROKER_ORDERS = False

LIVE_BROKER_ENABLED = False

DEFAULT_SYMBOL = "NIFTY"
DEFAULT_QUANTITY = 1

MAX_QUANTITY = 10
MAX_ORDER_VALUE = 100000.0
MAX_SESSION_TRADES = 20
MAX_SESSION_LOSS = 5000.0

ENABLE_KILL_SWITCH = True
KILL_SWITCH_DEFAULT = False

REQUIRE_BROKER_HEALTH = True
REQUIRE_POSITION_RECONCILIATION = True
REQUIRE_ORDER_IDEMPOTENCY = True

REPORT_DIRECTORY = "reports/phase21"

REPORT_FILENAME = (
    "phase21_execution_certification_report.json"
)

AUDIT_FILENAME = (
    "phase21_execution_audit.log"
)

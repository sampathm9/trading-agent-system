from pathlib import Path


# ---------------------------------------------------------
# PHASE 16
# ---------------------------------------------------------

INITIAL_CAPITAL = 100000.0

DEFAULT_QUANTITY = 1

QUANTITY_VALUES = [
    1,
    2,
    3,
    4,
    5,
]

MIN_AI_CONFIDENCE_VALUES = [
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
]

MIN_TRADES_FOR_FULL_SCORE = 1

REPORT_DIRECTORY = (
    Path("reports") / "phase16"
)

REPORT_FILENAME = (
    "phase16_optimization_report.json"
)

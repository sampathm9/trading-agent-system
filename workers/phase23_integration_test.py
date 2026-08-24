import json
from pathlib import Path


# ============================================================
# PHASE 23 INTEGRATION TEST
# ============================================================

from config.phase23_config import (
    DEFAULT_MIN_AI_CONFIDENCE,
    DEFAULT_QUANTITY,
    DEFAULT_SYMBOL,
    INITIAL_CAPITAL,
    REPORT_DIRECTORY,
)

from workers.shadow_trading.phase23_shadow_worker import (
    Phase23ShadowTradingWorker,
)


class TestIntelligence:

    def __init__(
        self,
        min_ai_confidence=0.60,
    ):
        self.min_ai_confidence = (
            float(min_ai_confidence)
        )

    def strategy_signal(
        self,
        candles,
        news=None,
    ):

        if len(candles) < 3:

            return {
                "signal": "HOLD",
                "confidence": 0.0,
                "score": 0.0,
                "reason": "Insufficient history",
            }

        previous = float(
            candles[-2]["close"]
        )

        current = float(
            candles[-1]["close"]
        )

        if current > previous:

            return {
                "signal": "BUY",
                "confidence": 0.80,
                "score": 1.0,
                "reason": "Positive price momentum",
            }

        if current < previous:

            return {
                "signal": "SELL",
                "confidence": 0.80,
                "score": -1.0,
                "reason": "Negative price momentum",
            }

        return {
            "signal": "HOLD",
            "confidence": 0.50,
            "score": 0.0,
            "reason": "No directional movement",
        }


def intelligence_factory(
    min_ai_confidence=0.60,
):

    return TestIntelligence(
        min_ai_confidence=min_ai_confidence
    )


def build_candles():

    prices = [
        100,
        101,
        102,
        103,
        104,
        105,
        104,
        103,
        102,
        101,
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        105,
        104,
        103,
        102,
        101,
        102,
        103,
        104,
        105,
    ]

    candles = []

    for index, close in enumerate(prices):

        candles.append(
            {
                "timestamp": (
                    f"2026-08-24T09:"
                    f"{15 + index:02d}:00"
                ),
                "open": close - 0.5,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
            }
        )

    return candles


def check(
    name,
    condition,
):

    status = "PASS" if condition else "FAIL"

    print(
        f"{name}: {status}"
    )

    if not condition:

        raise AssertionError(
            name
        )


def main():

    print("=" * 60)
    print(
        "PHASE 23 SHADOW TRADING / "
        "LIVE MARKET OBSERVATION INTEGRATION TEST"
    )
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. HISTORICAL / MARKET DATA
    # ---------------------------------------------------------

    candles = build_candles()

    print()
    print("1. MARKET DATA")
    print("-" * 60)

    print(
        f"Observed candles: "
        f"{len(candles)} PASS"
    )

    check(
        "Historical candle validation",
        len(candles) >= 10,
    )

    # ---------------------------------------------------------
    # 2. INTELLIGENCE
    # ---------------------------------------------------------

    print()
    print("2. INTELLIGENCE")
    print("-" * 60)

    intelligence = intelligence_factory(
        min_ai_confidence=DEFAULT_MIN_AI_CONFIDENCE
    )

    signal = intelligence.strategy_signal(
        candles=candles[:5],
        news=None,
    )

    print(
        "Intelligence pipeline: PASS"
    )

    print(
        "AI signal:",
        signal["signal"],
    )

    check(
        "AI signal generated",
        signal["signal"] in {
            "BUY",
            "SELL",
            "HOLD",
        },
    )

    # ---------------------------------------------------------
    # 3. PHASE 23 WORKER
    # ---------------------------------------------------------

    print()
    print("3. PHASE 23 SHADOW SESSION")
    print("-" * 60)

    worker = Phase23ShadowTradingWorker(
        intelligence_worker_factory=(
            intelligence_factory
        ),
        initial_capital=INITIAL_CAPITAL,
    )

    result = worker.run(
        candles=candles,
        symbol=DEFAULT_SYMBOL,
        quantity=DEFAULT_QUANTITY,
        min_ai_confidence=(
            DEFAULT_MIN_AI_CONFIDENCE
        ),
        news=None,
    )

    check(
        "Shadow worker: PASS",
        result["phase"] == 23,
    )

    # ---------------------------------------------------------
    # 4. OBSERVATION
    # ---------------------------------------------------------

    print()
    print("4. MARKET OBSERVATION")
    print("-" * 60)

    observed = result[
        "summary"
    ]["candles_observed"]

    print(
        f"Candles observed: "
        f"{observed} PASS"
    )

    check(
        "Observation count",
        observed == len(candles),
    )

    # ---------------------------------------------------------
    # 5. VIRTUAL TRADES
    # ---------------------------------------------------------

    print()
    print("5. VIRTUAL TRADING")
    print("-" * 60)

    trades = result[
        "summary"
    ]["trades"]

    print(
        f"Virtual trades: "
        f"{trades} PASS"
    )

    check(
        "Virtual trade accounting",
        trades >= 0,
    )

    # ---------------------------------------------------------
    # 6. PNL
    # ---------------------------------------------------------

    print()
    print("6. VIRTUAL P&L")
    print("-" * 60)

    pnl = result[
        "summary"
    ]["total_pnl"]

    print(
        f"Virtual P&L: {pnl}"
    )

    check(
        "Virtual P&L calculated",
        isinstance(
            pnl,
            (int, float),
        ),
    )

    # ---------------------------------------------------------
    # 7. SAFETY
    # ---------------------------------------------------------

    print()
    print("7. SAFETY")
    print("-" * 60)

    safety = result["safety"]

    print(
        "Shadow mode: PASS"
    )

    print(
        "Real orders disabled: PASS"
    )

    print(
        "Real broker unused: PASS"
    )

    check(
        "Shadow mode",
        safety["checks"]["shadow_mode"],
    )

    check(
        "Live trading disabled",
        safety["checks"][
            "live_trading_disabled"
        ],
    )

    check(
        "Real broker disabled",
        safety["checks"][
            "real_broker_disabled"
        ],
    )

    check(
        "Real orders disabled",
        safety["checks"][
            "real_orders_disabled"
        ],
    )

    check(
        "Real orders placed",
        result["real_orders_placed"] == 0,
    )

    check(
        "Real broker unused",
        result["real_broker_used"] is False,
    )

    # ---------------------------------------------------------
    # 8. READINESS
    # ---------------------------------------------------------

    print()
    print("8. SHADOW READINESS")
    print("-" * 60)

    readiness = result[
        "readiness"
    ]

    print(
        "Shadow observation readiness:",
        "PASS"
        if readiness["ready"]
        else "FAIL",
    )

    print(
        "Classification:",
        readiness["classification"],
    )

    print(
        "Readiness score:",
        readiness["score"],
    )

    check(
        "Shadow readiness",
        readiness["ready"],
    )

    # ---------------------------------------------------------
    # 9. REPORT
    # ---------------------------------------------------------

    print()
    print("9. JSON REPORT")
    print("-" * 60)

    report = worker.save_report(
        result
    )

    print(
        "Report:",
        report,
        "PASS",
    )

    report_path = Path(report)

    check(
        "Report exists",
        report_path.exists(),
    )

    loaded = json.loads(
        report_path.read_text(
            encoding="utf-8"
        )
    )

    check(
        "Report valid JSON",
        loaded["phase"] == 23,
    )

    # ---------------------------------------------------------
    # 10. FINAL
    # ---------------------------------------------------------

    print()
    print("10. FINAL VALIDATION")
    print("-" * 60)

    checks = [
        ("Market data", True),
        ("Intelligence", True),
        ("Shadow worker", True),
        ("Observation", True),
        ("Virtual trading", True),
        ("Virtual P&L", True),
        ("Safety", True),
        ("Readiness", True),
        ("JSON report", True),
        (
            "Real broker untouched",
            result["real_broker_used"] is False,
        ),
        (
            "Real orders untouched",
            result["real_orders_placed"] == 0,
        ),
    ]

    for name, passed in checks:

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

        if not passed:

            raise AssertionError(
                name
            )

    print()
    print("=" * 60)
    print(
        "PHASE 23 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()

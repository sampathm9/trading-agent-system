import json
from pathlib import Path

from workers.integration import (
    IntelligentTradingWorker,
)

from workers.broker.paper_broker import (
    PaperBroker,
)

from workers.execution.execution_worker import (
    ExecutionWorker,
)

from workers.broker.models import (
    OrderStatus,
)


def build_bullish_candles():

    candles = []

    price = 100.0

    for index in range(40):

        open_price = price
        close_price = price + 1.0
        high_price = close_price + 0.5
        low_price = open_price - 0.5

        candles.append(
            {
                "timestamp": (
                    f"2026-08-24T09:"
                    f"{index:02d}:00"
                ),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": 1000 + index,
            }
        )

        price = close_price

    return candles


def build_news():

    return [
        {
            "title": (
                "NIFTY shows strong growth "
                "and bullish market momentum"
            )
        },
        {
            "title": (
                "Markets rally as investors "
                "remain optimistic"
            )
        },
    ]


def main():

    print("=" * 60)
    print("PHASE 13 INTELLIGENCE TO EXECUTION INTEGRATION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. MARKET DATA
    # ---------------------------------------------------------

    print("\n1. MARKET DATA")
    print("-" * 60)

    candles = build_bullish_candles()
    news = build_news()

    assert len(candles) == 40

    print(
        "Candles:",
        len(candles),
        "PASS",
    )

    # ---------------------------------------------------------
    # 2. PAPER BROKER
    # ---------------------------------------------------------

    print("\n2. PAPER BROKER")
    print("-" * 60)

    broker = PaperBroker()

    execution = ExecutionWorker(
        broker
    )

    assert broker.is_connected() is True

    print(
        "Paper broker connected: PASS"
    )

    # ---------------------------------------------------------
    # 3. INTELLIGENT WORKER
    # ---------------------------------------------------------

    print("\n3. INTELLIGENCE WORKER")
    print("-" * 60)

    worker = IntelligentTradingWorker(
        execution_worker=execution
    )

    intelligence = worker.analyze_market(
        candles,
        news,
    )

    assert "technical" in intelligence
    assert "regime" in intelligence
    assert "sentiment" in intelligence
    assert "ai" in intelligence

    print(
        "Technical analysis: PASS"
    )

    print(
        "Market regime:",
        intelligence["regime"]["regime"],
    )

    print(
        "Sentiment:",
        intelligence["sentiment"]["label"],
    )

    print(
        "AI signal:",
        intelligence["ai"]["signal"],
    )

    print(
        "AI confidence:",
        intelligence["ai"]["confidence"],
    )

    print(
        "Intelligence pipeline: PASS"
    )

    # ---------------------------------------------------------
    # 4. STRATEGY
    # ---------------------------------------------------------

    print("\n4. STRATEGY")
    print("-" * 60)

    strategy = worker.create_strategy_signal(
        intelligence
    )

    assert strategy["action"] in {
        "BUY",
        "SELL",
        "HOLD",
        "NO_TRADE",
    }

    assert 0.0 <= strategy["confidence"] <= 1.0

    print(
        "AI signal:",
        strategy["signal"],
    )

    print(
        "Strategy action:",
        strategy["action"],
    )

    print(
        "Strategy confidence:",
        strategy["confidence"],
    )

    print(
        "Strategy integration: PASS"
    )

    # ---------------------------------------------------------
    # 5. RISK
    # ---------------------------------------------------------

    print("\n5. RISK")
    print("-" * 60)

    risk = worker.validate_risk(
        strategy,
        quantity=1,
    )

    assert risk["approved"] is True

    print(
        "Risk approved:",
        risk["approved"],
    )

    print(
        "Risk validation: PASS"
    )

    # ---------------------------------------------------------
    # 6. COMPLETE CYCLE
    # ---------------------------------------------------------

    print("\n6. COMPLETE DECISION CYCLE")
    print("-" * 60)

    cycle = worker.run_cycle(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        price=100.0,
        news=news,
    )

    assert cycle["intelligence"]["ai"]["signal"] == "BUY"
    assert cycle["strategy"]["action"] == "BUY"
    assert cycle["risk"]["approved"] is True

    execution_result = cycle["execution"]

    assert execution_result is not None
    assert (
        execution_result.status
        == OrderStatus.FILLED
    )

    assert (
        execution_result.price
        == 100.0
    )

    print(
        "AI → Strategy → Risk → Execution: PASS"
    )

    print(
        "Execution status:",
        execution_result.status.value,
    )

    # ---------------------------------------------------------
    # 7. POSITION
    # ---------------------------------------------------------

    print("\n7. POSITION")
    print("-" * 60)

    positions = worker.positions()

    assert "NIFTY" in positions
    assert positions["NIFTY"]["quantity"] == 1

    print(
        "Position:",
        positions,
    )

    print(
        "Position tracking: PASS"
    )

    # ---------------------------------------------------------
    # 8. EOD EXIT
    # ---------------------------------------------------------

    print("\n8. EOD EXIT")
    print("-" * 60)

    eod_results = worker.close_all(
        {
            "NIFTY": 105.0,
        }
    )

    assert len(eod_results) == 1

    eod = eod_results[0]

    assert (
        eod.status
        == OrderStatus.FILLED
    )

    assert eod.realized_pnl == 5.0

    assert worker.positions() == {}

    print(
        "EOD order:",
        eod.status.value,
    )

    print(
        "EOD realized P&L:",
        eod.realized_pnl,
    )

    print(
        "EOD exit: PASS"
    )

    # ---------------------------------------------------------
    # 9. RISK REJECTION
    # ---------------------------------------------------------

    print("\n9. RISK REJECTION")
    print("-" * 60)

    rejected = worker.risk.validate(
        "BUY",
        101,
        max_quantity=100,
    )

    assert rejected is False

    print(
        "Oversized quantity rejected: PASS"
    )

    invalid_action = worker.risk.validate(
        "HOLD",
        1,
        max_quantity=100,
    )

    assert invalid_action is False

    print(
        "Non-trading action rejected: PASS"
    )

    # ---------------------------------------------------------
    # 10. NO DIRECT BROKER FROM INTELLIGENCE
    # ---------------------------------------------------------

    print("\n10. ARCHITECTURE SAFETY")
    print("-" * 60)

    intelligence_worker = worker.intelligence

    assert not hasattr(
        intelligence_worker,
        "broker",
    )

    assert not hasattr(
        intelligence_worker,
        "execution_worker",
    )

    print(
        "Intelligence has no broker reference: PASS"
    )

    print(
        "Intelligence remains read-only: PASS"
    )

    # ---------------------------------------------------------
    # 11. REPORT
    # ---------------------------------------------------------

    print("\n11. JSON REPORT")
    print("-" * 60)

    report_path = Path(
        "reports/phase13/"
        "phase13_intelligence_execution_report.json"
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "phase": 13,
        "name": (
            "Intelligence to Strategy "
            "to Risk to Paper Execution"
        ),
        "status": "PASS",
        "candles": len(candles),
        "symbol": "NIFTY",
        "quantity": 1,
        "intelligence": {
            "technical": intelligence[
                "technical"
            ],
            "regime": intelligence[
                "regime"
            ],
            "sentiment": intelligence[
                "sentiment"
            ],
            "ai": intelligence[
                "ai"
            ],
        },
        "strategy": strategy,
        "risk": risk,
        "execution": {
            "status": (
                execution_result.status.value
            ),
            "price": execution_result.price,
            "realized_pnl": (
                execution_result.realized_pnl
            ),
        },
        "eod": {
            "status": eod.status.value,
            "price": eod.price,
            "realized_pnl": eod.realized_pnl,
        },
        "final_positions": worker.positions(),
        "safety": {
            "paper_broker_only": True,
            "real_broker_used": False,
            "intelligence_read_only": True,
        },
    }

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    assert report_path.exists()

    print(
        "Report:",
        report_path,
    )

    print(
        "Report generation: PASS"
    )

    # ---------------------------------------------------------
    # 12. FINAL VALIDATION
    # ---------------------------------------------------------

    print("\n12. FINAL VALIDATION")
    print("-" * 60)

    print(
        "Market data: PASS"
    )

    print(
        "Technical intelligence: PASS"
    )

    print(
        "Market regime: PASS"
    )

    print(
        "Sentiment: PASS"
    )

    print(
        "AI analysis: PASS"
    )

    print(
        "Strategy integration: PASS"
    )

    print(
        "Risk integration: PASS"
    )

    print(
        "Paper execution: PASS"
    )

    print(
        "Position tracking: PASS"
    )

    print(
        "EOD exit: PASS"
    )

    print(
        "Risk rejection: PASS"
    )

    print(
        "Real broker untouched: PASS"
    )

    print(
        "Architecture safety: PASS"
    )

    print()
    print("=" * 60)
    print("PHASE 13 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

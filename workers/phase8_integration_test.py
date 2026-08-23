from datetime import date

from agents.daily_trading_agent import DailyTradingAgent

from workers.calendar.market_calendar import (
    NSEMarketCalendar
)

from workers.pipeline.trading_pipeline import (
    TradingPipeline
)

from workers.runtime.paper_runtime import (
    PaperTradingRuntime
)

from workers.strategy.strategy_engine import (
    StrategyEngine
)

from workers.orchestrator.trading_session_orchestrator import (
    TradingSessionOrchestrator
)


def build_candles():

    candles = []

    for i in range(30):

        close = 100 + i

        candles.append(
            {
                "timestamp":
                    f"2026-08-24T09:{15 + i:02d}:00",

                "open": close - 1,
                "high": close + 1,
                "low": close - 2,
                "close": close,
                "volume": 0,
            }
        )

    return candles


class TestMarketDataWorker:

    def __init__(self, candles):

        self.candles = candles

    def get_candles(self, symbol):

        return list(self.candles)


def main():

    print("=" * 60)
    print("PHASE 8 SESSION ORCHESTRATOR INTEGRATION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. BUILD COMPONENTS
    # ---------------------------------------------------------

    print()
    print("1. BUILD COMPONENTS")
    print("-" * 60)

    agent = DailyTradingAgent()

    candles = build_candles()

    agent.load_market_data(
        "NIFTY",
        candles
    )

    runtime = PaperTradingRuntime(
        agent=agent,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
        quantity=1,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000,
    )

    market_data_worker = TestMarketDataWorker(
        candles
    )

    strategy_engine = StrategyEngine()

    pipeline = TradingPipeline(
        runtime=runtime,
        market_data_worker=market_data_worker,
        strategy_engine=strategy_engine,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
    )

    orchestrator = TradingSessionOrchestrator(
        pipeline=pipeline,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
    )

    print("Components created")

    # ---------------------------------------------------------
    # 2. WEEKEND PROTECTION
    # ---------------------------------------------------------

    print()
    print("2. WEEKEND PROTECTION")
    print("-" * 60)

    weekend = orchestrator.start(
        date(2026, 8, 23)
    )

    print(weekend)

    assert weekend["status"] == "MARKET_CLOSED"

    print("Weekend protection: PASS")

    # ---------------------------------------------------------
    # 3. SESSION START
    # ---------------------------------------------------------

    print()
    print("3. SESSION START")
    print("-" * 60)

    start = orchestrator.start(
        date(2026, 8, 24)
    )

    print(start)

    assert start["status"] == "STARTED"
    assert orchestrator.phase == "PRE_MARKET"

    print("Session start: PASS")

    # ---------------------------------------------------------
    # 4. MARKET OPEN
    # ---------------------------------------------------------

    print()
    print("4. MARKET OPEN")
    print("-" * 60)

    opened = orchestrator.open_market()

    print(opened)

    assert opened["status"] == "COMPLETED"
    assert opened["phase"] == "MARKET_OPEN"

    print("Market open: PASS")

    # ---------------------------------------------------------
    # 5. ENABLE TRADING
    # ---------------------------------------------------------

    print()
    print("5. ENABLE TRADING")
    print("-" * 60)

    trading = orchestrator.enable_trading()

    print(trading)

    assert trading["status"] == "COMPLETED"
    assert orchestrator.phase == "TRADING"
    assert runtime.entries_enabled is True

    print("Trading enabled: PASS")

    # ---------------------------------------------------------
    # 6. MARKET DATA
    # ---------------------------------------------------------

    print()
    print("6. MARKET DATA")
    print("-" * 60)

    data = orchestrator.get_market_data()

    print(
        "Candles:",
        data["count"]
    )

    assert data["status"] == "COMPLETED"
    assert data["count"] == 30

    print("Market data: PASS")

    # ---------------------------------------------------------
    # 7. STRATEGY
    # ---------------------------------------------------------

    print()
    print("7. STRATEGY")
    print("-" * 60)

    strategy = orchestrator.run_strategy(
        data["candles"]
    )

    print(strategy)

    assert strategy["status"] == "COMPLETED"
    assert strategy["trend"]["trend"] == "BULLISH"
    assert strategy["signal"]["action"] == "BUY"

    print("Strategy: PASS")

    # ---------------------------------------------------------
    # 8. ENTRY
    # ---------------------------------------------------------

    print()
    print("8. ENTRY")
    print("-" * 60)

    entry = orchestrator.run_entry()

    print(entry)

    assert entry["status"] == "EXECUTED"

    position = runtime.get_position()

    print(
        "Position:",
        position
    )

    assert position is not None

    entry_price = position["entry_price"]

    print("Entry execution: PASS")

    # ---------------------------------------------------------
    # 9. POSITION MONITOR
    # ---------------------------------------------------------

    print()
    print("9. POSITION MONITOR")
    print("-" * 60)

    monitor = orchestrator.monitor_position(
        entry_price * 1.01
    )

    print(monitor)

    assert monitor["status"] == "HOLD"

    print("Position monitor: PASS")

    # ---------------------------------------------------------
    # 10. TAKE PROFIT
    # ---------------------------------------------------------

    print()
    print("10. TAKE PROFIT")
    print("-" * 60)

    take_profit = orchestrator.monitor_position(
        entry_price * 1.05
    )

    print(take_profit)

    assert take_profit["status"] == "TAKE_PROFIT"

    assert runtime.get_position() is None

    print("Take profit: PASS")

    # ---------------------------------------------------------
    # 11. ENTRY CUTOFF
    # ---------------------------------------------------------

    print()
    print("11. ENTRY CUTOFF")
    print("-" * 60)

    cutoff = orchestrator.stop_entries()

    print(cutoff)

    assert cutoff["status"] == "COMPLETED"
    assert orchestrator.phase == "ENTRY_CUTOFF"
    assert runtime.entries_enabled is False

    print("Entry cutoff: PASS")

    # ---------------------------------------------------------
    # 12. EOD SAFETY
    # ---------------------------------------------------------

    print()
    print("12. EOD SAFETY")
    print("-" * 60)

    eod = orchestrator.eod_exit(
        entry_price * 1.05
    )

    print(eod)

    assert eod["status"] == "NO_POSITION"

    print("EOD safety: PASS")

    # ---------------------------------------------------------
    # 13. SESSION STATE
    # ---------------------------------------------------------

    print()
    print("13. SESSION STATE")
    print("-" * 60)

    state = orchestrator.get_state()

    print(state)

    assert state["running"] is True
    assert state["phase"] == "MARKET_CLOSE"
    assert state["symbol"] == "NIFTY"

    print("Session state: PASS")

    # ---------------------------------------------------------
    # 14. STOP
    # ---------------------------------------------------------

    print()
    print("14. SESSION STOP")
    print("-" * 60)

    stopped = orchestrator.stop()

    print(stopped)

    assert stopped["status"] == "STOPPED"
    assert orchestrator.running is False
    assert orchestrator.phase == "CLOSED"

    print("Session stop: PASS")

    # ---------------------------------------------------------
    # 15. EVENTS
    # ---------------------------------------------------------

    print()
    print("15. EVENTS")
    print("-" * 60)

    print(
        "Total orchestrator events:",
        len(orchestrator.events)
    )

    for event in orchestrator.events:
        print(event)

    assert len(orchestrator.events) > 0

    print("Event logging: PASS")

    # ---------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("PHASE 8 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

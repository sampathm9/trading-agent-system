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

from workers.intraday.candle_replay import (
    CandleReplay
)

from workers.intraday.intraday_controller import (
    IntradayController
)


class TestMarketDataWorker:

    def __init__(self, candles):

        self.candles = list(candles)

    def get_candles(self, symbol):

        return list(self.candles)


def main():

    print("=" * 60)
    print("PHASE 9 INTRADAY CONTROLLER INTEGRATION TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. BUILD COMPONENTS
    # ---------------------------------------------------------

    print()
    print("1. BUILD COMPONENTS")
    print("-" * 60)

    candles = CandleReplay.build_test_day()

    agent = DailyTradingAgent()

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

    controller = IntradayController(
        pipeline=pipeline,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
        entry_cutoff="15:00",
        market_close="15:30",
    )

    print(
        "Components created"
    )

    print(
        "Replay candles:",
        len(candles)
    )

    assert len(candles) == 76

    # ---------------------------------------------------------
    # 2. WEEKEND PROTECTION
    # ---------------------------------------------------------

    print()
    print("2. WEEKEND PROTECTION")
    print("-" * 60)

    weekend = controller.start(
        date(2026, 8, 23)
    )

    print(weekend)

    assert (
        weekend["status"]
        == "MARKET_CLOSED"
    )

    print(
        "Weekend protection: PASS"
    )

    # ---------------------------------------------------------
    # 3. SESSION START
    # ---------------------------------------------------------

    print()
    print("3. SESSION START")
    print("-" * 60)

    started = controller.start(
        date(2026, 8, 24)
    )

    print(started)

    assert (
        started["status"]
        == "STARTED"
    )

    assert controller.running is True

    print(
        "Session start: PASS"
    )

    # ---------------------------------------------------------
    # 4. LOAD REPLAY
    # ---------------------------------------------------------

    print()
    print("4. CANDLE REPLAY")
    print("-" * 60)

    replay = controller.load_replay(
        candles
    )

    print(
        "Replay size:",
        len(replay)
    )

    assert len(replay) == 76
    assert replay.has_next() is True

    print(
        "Replay initialization: PASS"
    )

    # ---------------------------------------------------------
    # 5. RUN INTRADAY SESSION
    # ---------------------------------------------------------

    print()
    print("5. INTRADAY SESSION")
    print("-" * 60)

    result = controller.run_replay(
        replay
    )

    print(
        "Replay status:",
        result["status"]
    )

    print(
        "Processed candles:",
        result["processed_candles"]
    )

    print(
        "Trades:",
        result["trades"]
    )

    assert (
        result["status"]
        == "COMPLETED"
    )

    assert (
        result["processed_candles"]
        == 76
    )

    print(
        "Intraday replay: PASS"
    )

    # ---------------------------------------------------------
    # 6. VERIFY ENTRY
    # ---------------------------------------------------------

    print()
    print("6. ENTRY")
    print("-" * 60)

    entries = [
        trade
        for trade in controller.trades
        if trade["side"] == "BUY"
    ]

    print(
        "Entries:",
        len(entries)
    )

    assert len(entries) >= 1

    print(
        "Entry generation: PASS"
    )

    # ---------------------------------------------------------
    # 7. VERIFY EXIT
    # ---------------------------------------------------------

    print()
    print("7. POSITION EXIT")
    print("-" * 60)

    exits = [
        trade
        for trade in controller.trades
        if trade["side"] == "SELL"
    ]

    print(
        "Exits:",
        len(exits)
    )

    assert len(exits) >= 1

    print(
        "Position exit: PASS"
    )

    # ---------------------------------------------------------
    # 8. ENTRY CUTOFF
    # ---------------------------------------------------------

    print()
    print("8. ENTRY CUTOFF")
    print("-" * 60)

    print(
        "Entries stopped:",
        controller.entries_stopped
    )

    assert (
        controller.entries_stopped
        is True
    )

    cutoff_events = [
        event
        for event in controller.events
        if event["event"]
        == "ENTRY_CUTOFF_REACHED"
    ]

    print(
        "Cutoff events:",
        len(cutoff_events)
    )

    assert len(cutoff_events) >= 1

    print(
        "Entry cutoff protection: PASS"
    )

    # ---------------------------------------------------------
    # 9. EOD
    # ---------------------------------------------------------

    print()
    print("9. EOD SAFETY")
    print("-" * 60)

    eod_events = [
        event
        for event in controller.events
        if event["event"]
        == "EOD_EXIT"
    ]

    print(
        "EOD events:",
        len(eod_events)
    )

    assert len(eod_events) >= 1

    assert (
        runtime.get_position()
        is None
    )

    print(
        "EOD safety: PASS"
    )

    # ---------------------------------------------------------
    # 10. P&L
    # ---------------------------------------------------------

    print()
    print("10. P&L")
    print("-" * 60)

    state = runtime.get_state()

    print(
        "Realized P&L:",
        state["realized_pnl"]
    )

    assert (
        state["position"]
        is None
    )

    print(
        "P&L tracking: PASS"
    )

    # ---------------------------------------------------------
    # 11. REPORTS
    # ---------------------------------------------------------

    print()
    print("11. REPORTS")
    print("-" * 60)

    reports = controller.save_reports(
        "reports/phase9"
    )

    print(
        "JSON:",
        reports["json"]
    )

    print(
        "CSV:",
        reports["events_csv"]
    )

    print(
        "Trades:",
        reports["trades_csv"]
    )

    # ---------------------------------------------------------
    # 12. EVENTS
    # ---------------------------------------------------------

    print()
    print("12. EVENT HISTORY")
    print("-" * 60)

    print(
        "Total events:",
        len(controller.events)
    )

    assert (
        len(controller.events)
        > 0
    )

    required_events = {
        "SESSION_STARTED",
        "REPLAY_LOADED",
        "CANDLE_RECEIVED",
        "STRATEGY_EVALUATED",
        "ENTRY_EVALUATED",
        "ENTRY_CUTOFF_REACHED",
        "EOD_EXIT",
        "REPLAY_COMPLETED",
    }

    actual_events = {
        event["event"]
        for event in controller.events
    }

    missing = (
        required_events
        - actual_events
    )

    print(
        "Missing events:",
        missing
    )

    assert not missing

    print(
        "Event history: PASS"
    )

    # ---------------------------------------------------------
    # 13. STOP
    # ---------------------------------------------------------

    print()
    print("13. SHUTDOWN")
    print("-" * 60)

    stopped = controller.stop()

    print(stopped)

    assert (
        controller.running
        is False
    )

    print(
        "Shutdown: PASS"
    )

    # ---------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("PHASE 9 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

from datetime import date

from agents.daily_trading_agent import DailyTradingAgent
from workers.calendar.market_calendar import NSEMarketCalendar
from workers.runtime.paper_runtime import PaperTradingRuntime


def build_candles():

    candles = []

    for i in range(22):

        close = 100 + i

        candles.append(
            {
                "timestamp": (
                    f"2026-08-24T09:{15+i:02d}:00"
                ),
                "open": close - 1,
                "high": close + 1,
                "low": close - 2,
                "close": close,
            }
        )

    return candles


def main():

    print("=" * 60)
    print("PHASE 4 COMPLETE INTEGRATION TEST")
    print("=" * 60)

    print()
    print("1. CREATE AGENT")
    print("-" * 60)

    agent = DailyTradingAgent()

    print("DailyTradingAgent created")

    print()
    print("2. LOAD MARKET DATA")
    print("-" * 60)

    candles = build_candles()

    agent.load_market_data(
        "NIFTY",
        candles
    )

    print("Candles loaded:", len(candles))

    assert len(candles) == 22

    print()
    print("3. CREATE PAPER RUNTIME")
    print("-" * 60)

    runtime = PaperTradingRuntime(
        agent=agent,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
        quantity=1,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000,
    )

    print("Runtime created")

    print()
    print("4. MARKET DAY PROTECTION")
    print("-" * 60)

    weekend = runtime.start(
        date(2026, 8, 23)
    )

    print("Weekend:", weekend)

    assert weekend["status"] == "MARKET_CLOSED"

    trading_day = runtime.start(
        date(2026, 8, 24)
    )

    print("Trading day:", trading_day)

    assert trading_day["status"] == "STARTED"

    print()
    print("5. TRADING ENTRY")
    print("-" * 60)

    entry = runtime.run_entry_cycle()

    print("Entry:", entry)

    assert entry["status"] == "EXECUTED"

    position = runtime.get_position()

    print("Position:", position)

    assert position is not None

    print()
    print("6. POSITION MONITOR")
    print("-" * 60)

    entry_price = position["entry_price"]

    monitor = runtime.monitor_position(
        entry_price * 1.01
    )

    print("Monitor:", monitor)

    assert monitor["status"] == "HOLD"

    print()
    print("7. TAKE PROFIT")
    print("-" * 60)

    take_profit = runtime.monitor_position(
        entry_price * 1.05
    )

    print("Take profit:", take_profit)

    assert take_profit["status"] == "TAKE_PROFIT"

    print()
    print("8. EOD SAFETY")
    print("-" * 60)

    eod = runtime.eod_exit(
        entry_price * 1.05
    )

    print("EOD:", eod)

    assert eod["status"] == "NO_POSITION"

    print()
    print("9. FINAL STATE")
    print("-" * 60)

    state = runtime.get_state()

    print(state)

    assert state["position"] is None
    assert state["running"] is True

    runtime.stop()

    print()
    print("10. RUNTIME EVENTS")
    print("-" * 60)

    for event in runtime.events:
        print(event)

    assert len(runtime.events) > 0

    print()
    print("=" * 60)
    print("PHASE 4 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

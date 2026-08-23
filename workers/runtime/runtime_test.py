from datetime import date

from agents.daily_trading_agent import DailyTradingAgent
from workers.calendar.market_calendar import NSEMarketCalendar
from workers.runtime.paper_runtime import PaperTradingRuntime


def candles():
    return [
        {"timestamp": f"2026-08-24T09:{15+i:02d}:00", "open": 100+i, "high": 102+i, "low": 99+i, "close": 100+i}
        for i in range(22)
    ]


def main():

    print("=" * 60)
    print("PHASE 4 PAPER RUNTIME TEST")
    print("=" * 60)

    calendar = NSEMarketCalendar()

    agent = DailyTradingAgent()

    agent.load_market_data(
        "NIFTY",
        candles()
    )

    runtime = PaperTradingRuntime(
        agent=agent,
        market_calendar=calendar,
        symbol="NIFTY",
        quantity=1,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000,
    )

    print()
    print("1. WEEKEND PROTECTION")
    print("-" * 60)

    weekend = runtime.start(
        date(2026, 8, 23)
    )

    print("Result:", weekend)

    assert weekend["status"] == "MARKET_CLOSED"
    assert runtime.running is False

    print("Weekend trading blocked: True")

    print()
    print("2. TRADING DAY START")
    print("-" * 60)

    start = runtime.start(
        date(2026, 8, 24)
    )

    print("Result:", start)

    assert start["status"] == "STARTED"
    assert runtime.running is True

    print()
    print("3. ENTRY")
    print("-" * 60)

    entry = runtime.run_entry_cycle()

    print("Entry:", entry)

    assert entry["status"] == "EXECUTED"

    position = runtime.get_position()

    print("Position:", position)

    assert position is not None

    print()
    print("4. POSITION MONITOR")
    print("-" * 60)

    entry_price = position["entry_price"]

    hold_price = entry_price * 1.01

    monitor = runtime.monitor_position(
        hold_price
    )

    print("Monitor:", monitor)

    assert monitor["status"] == "HOLD"

    print()
    print("5. TAKE PROFIT")
    print("-" * 60)

    target_price = entry_price * 1.05

    take_profit = runtime.monitor_position(
        target_price
    )

    print("Result:", take_profit)

    assert take_profit["status"] == "TAKE_PROFIT"

    assert runtime.get_position() is None

    print()
    print("6. EOD EXIT WITH NO POSITION")
    print("-" * 60)

    eod = runtime.eod_exit(
        target_price
    )

    print("EOD:", eod)

    assert eod["status"] == "NO_POSITION"

    print()
    print("7. FINAL STATE")
    print("-" * 60)

    state = runtime.get_state()

    print(state)

    assert state["running"] is True

    runtime.stop()

    assert runtime.running is False

    print()
    print("=" * 60)
    print("PHASE 4 PAPER RUNTIME TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

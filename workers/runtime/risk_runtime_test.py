from datetime import date

from agents.daily_trading_agent import DailyTradingAgent
from workers.calendar.market_calendar import NSEMarketCalendar
from workers.runtime.paper_runtime import PaperTradingRuntime


def main():

    print("=" * 60)
    print("PHASE 4 DAILY LOSS RUNTIME TEST")
    print("=" * 60)

    agent = DailyTradingAgent()

    agent.load_market_data(
        "NIFTY",
        [
            {
                "timestamp": f"2026-08-24T09:{15+i:02d}:00",
                "open": 100 + i,
                "high": 102 + i,
                "low": 99 + i,
                "close": 100 + i,
            }
            for i in range(22)
        ],
    )

    runtime = PaperTradingRuntime(
        agent=agent,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
        quantity=1,
        max_daily_loss=5,
    )

    start = runtime.start(
        date(2026, 8, 24)
    )

    assert start["status"] == "STARTED"

    entry = runtime.run_entry_cycle()

    print("Entry:", entry)

    assert entry["status"] == "EXECUTED"

    position = runtime.get_position()

    assert position is not None

    entry_price = position["entry_price"]

    loss_price = entry_price - 10

    result = runtime.monitor_position(
        loss_price
    )

    print("Stop result:", result)

    assert result["status"] == "STOP_LOSS"

    print("Daily loss:", runtime.get_daily_loss())

    assert runtime.get_daily_loss() >= 5

    next_entry = runtime.run_entry_cycle()

    print("Next entry:", next_entry)

    assert next_entry["status"] == "DAILY_LOSS_LIMIT"

    runtime.stop()

    print("=" * 60)
    print("DAILY LOSS RUNTIME TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

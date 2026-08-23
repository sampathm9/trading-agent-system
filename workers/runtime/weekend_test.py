from datetime import date

from agents.daily_trading_agent import DailyTradingAgent
from workers.calendar.market_calendar import NSEMarketCalendar
from workers.runtime.paper_runtime import PaperTradingRuntime


def main():

    calendar = NSEMarketCalendar()
    agent = DailyTradingAgent()

    runtime = PaperTradingRuntime(
        agent=agent,
        market_calendar=calendar,
    )

    print("=" * 60)
    print("PHASE 4 WEEKEND SAFETY TEST")
    print("=" * 60)

    for test_date in [
        date(2026, 8, 22),
        date(2026, 8, 23),
    ]:

        result = runtime.start(test_date)

        print(
            f"{test_date}: {result}"
        )

        assert result["status"] == "MARKET_CLOSED"
        assert runtime.running is False

    print("=" * 60)
    print("WEEKEND SAFETY TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

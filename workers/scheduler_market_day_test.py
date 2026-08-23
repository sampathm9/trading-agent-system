from datetime import date

from agents.daily_trading_agent import DailyTradingAgent
from workers.calendar.market_calendar import NSEMarketCalendar


def main():

    print("=" * 60)
    print("SCHEDULER MARKET DAY TEST")
    print("=" * 60)

    calendar = NSEMarketCalendar()

    agent = DailyTradingAgent(
        market_calendar=calendar
    )

    print()
    print("SATURDAY")

    saturday = date(2026, 8, 22)

    print(
        "Trading day:",
        calendar.is_trading_day(saturday)
    )

    assert not calendar.is_trading_day(
        saturday
    )

    print()
    print("SUNDAY")

    sunday = date(2026, 8, 23)

    print(
        "Trading day:",
        calendar.is_trading_day(sunday)
    )

    assert not calendar.is_trading_day(
        sunday
    )

    print()
    print("MONDAY")

    monday = date(2026, 8, 24)

    print(
        "Trading day:",
        calendar.is_trading_day(monday)
    )

    assert calendar.is_trading_day(
        monday
    )

    print()
    print("=" * 60)
    print("SCHEDULER MARKET DAY TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
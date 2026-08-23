from datetime import date, time

from workers.calendar.market_calendar import NSEMarketCalendar


def main():

    print("=" * 60)
    print("NSE MARKET CALENDAR TEST")
    print("=" * 60)

    calendar = NSEMarketCalendar()

    tests = [
        (
            "Saturday",
            date(2026, 8, 22),
            False
        ),
        (
            "Sunday",
            date(2026, 8, 23),
            False
        ),
        (
            "Monday",
            date(2026, 8, 24),
            True
        ),
        (
            "Republic Day",
            date(2026, 1, 26),
            False
        ),
        (
            "Normal trading day",
            date(2026, 8, 21),
            True
        ),
        (
            "Diwali Laxmi Pujan",
            date(2026, 11, 8),
            False
        ),
    ]

    print()

    for name, test_date, expected in tests:

        result = calendar.is_trading_day(test_date)

        print(
            f"{name:25} "
            f"{test_date} "
            f"Trading={result}"
        )

        assert result == expected

    print()
    print("TIME TESTS")
    print("-" * 60)

    normal_day = date(2026, 8, 21)

    assert calendar.is_entry_allowed(
        time(10, 0),
        normal_day
    )

    assert not calendar.is_entry_allowed(
        time(15, 1),
        normal_day
    )

    assert calendar.is_market_open(
        time(12, 0),
        normal_day
    )

    assert not calendar.is_market_open(
        time(16, 0),
        normal_day
    )

    print("10:00 -> entry allowed: True")
    print("15:01 -> entry allowed: False")
    print("12:00 -> market open: True")
    print("16:00 -> market open: False")

    print()
    print("WEEKEND TIME TEST")

    assert not calendar.is_entry_allowed(
        time(10, 0),
        date(2026, 8, 23)
    )

    assert not calendar.is_market_open(
        time(12, 0),
        date(2026, 8, 23)
    )

    print("Sunday 10:00 -> entry allowed: False")
    print("Sunday 12:00 -> market open: False")

    print()
    print("NEXT TRADING DAY")

    next_day = calendar.next_trading_day(
        date(2026, 8, 23)
    )

    print(
        "After Sunday 2026-08-23:",
        next_day
    )

    assert next_day == date(2026, 8, 24)

    print()
    print("=" * 60)
    print("MARKET CALENDAR TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
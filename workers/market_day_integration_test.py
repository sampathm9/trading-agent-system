from datetime import date

from workers.calendar.market_calendar import NSEMarketCalendar


def main():

    print("=" * 60)
    print("MARKET DAY INTEGRATION TEST")
    print("=" * 60)

    calendar = NSEMarketCalendar()

    # -------------------------------------------------
    # WEEKEND
    # -------------------------------------------------

    print()
    print("TEST 1 - SATURDAY")
    print("-" * 60)

    saturday = date(2026, 8, 22)

    result = calendar.is_trading_day(
        saturday
    )

    print(
        "Date:",
        saturday
    )

    print(
        "Trading day:",
        result
    )

    assert result is False

    # -------------------------------------------------
    # SUNDAY
    # -------------------------------------------------

    print()
    print("TEST 2 - SUNDAY")
    print("-" * 60)

    sunday = date(2026, 8, 23)

    result = calendar.is_trading_day(
        sunday
    )

    print(
        "Date:",
        sunday
    )

    print(
        "Trading day:",
        result
    )

    assert result is False

    # -------------------------------------------------
    # NORMAL DAY
    # -------------------------------------------------

    print()
    print("TEST 3 - NORMAL TRADING DAY")
    print("-" * 60)

    monday = date(2026, 8, 24)

    result = calendar.is_trading_day(
        monday
    )

    print(
        "Date:",
        monday
    )

    print(
        "Trading day:",
        result
    )

    assert result is True

    # -------------------------------------------------
    # NSE HOLIDAY
    # -------------------------------------------------

    print()
    print("TEST 4 - NSE HOLIDAY")
    print("-" * 60)

    republic_day = date(
        2026,
        1,
        26
    )

    result = calendar.is_trading_day(
        republic_day
    )

    print(
        "Date:",
        republic_day
    )

    print(
        "Trading day:",
        result
    )

    assert result is False

    # -------------------------------------------------
    # MUHURAT DAY
    # -------------------------------------------------

    print()
    print("TEST 5 - DIWALI LAXMI PUJAN")
    print("-" * 60)

    diwali = date(
        2026,
        11,
        8
    )

    result = calendar.is_trading_day(
        diwali
    )

    print(
        "Date:",
        diwali
    )

    print(
        "Trading day:",
        result
    )

    assert result is False

    print()
    print("=" * 60)
    print("ALL MARKET DAY TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
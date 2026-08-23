from datetime import date, datetime, time, timedelta


class NSEMarketCalendar:

    HOLIDAYS_2026 = {
        date(2026, 1, 26): "Republic Day",
        date(2026, 3, 3): "Holi",
        date(2026, 3, 26): "Shri Ram Navami",
        date(2026, 3, 31): "Shri Mahavir Jayanti",
        date(2026, 4, 3): "Good Friday",
        date(2026, 4, 14): "Dr. Baba Saheb Ambedkar Jayanti",
        date(2026, 5, 1): "Maharashtra Day",
        date(2026, 5, 28): "Bakri Id",
        date(2026, 6, 26): "Muharram",
        date(2026, 9, 14): "Ganesh Chaturthi",
        date(2026, 10, 2): "Mahatma Gandhi Jayanti",
        date(2026, 10, 20): "Dussehra",
        date(2026, 11, 8): "Diwali Laxmi Pujan / Muhurat Trading",
        date(2026, 11, 10): "Diwali-Balipratipada",
        date(2026, 11, 24): "Prakash Gurpurb Sri Guru Nanak Dev",
        date(2026, 12, 25): "Christmas",
    }

    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)
    ENTRY_CUTOFF = time(15, 0)

    def __init__(self, holidays=None):

        self.holidays = dict(self.HOLIDAYS_2026)

        if holidays:
            self.holidays.update(holidays)

    # ---------------------------------------------------------
    # DATE
    # ---------------------------------------------------------

    def normalize_date(self, trading_date=None):

        if trading_date is None:
            return date.today()

        if isinstance(trading_date, datetime):
            return trading_date.date()

        return trading_date

    def is_weekend(self, trading_date):

        trading_date = self.normalize_date(trading_date)

        return trading_date.weekday() >= 5

    def is_holiday(self, trading_date):

        trading_date = self.normalize_date(trading_date)

        return trading_date in self.holidays

    def is_trading_day(self, trading_date=None):

        trading_date = self.normalize_date(trading_date)

        if self.is_weekend(trading_date):
            return False

        if self.is_holiday(trading_date):
            return False

        return True

    def get_market_day_reason(self, trading_date=None):

        trading_date = self.normalize_date(trading_date)

        if self.is_weekend(trading_date):
            return "WEEKEND"

        if self.is_holiday(trading_date):
            return f"HOLIDAY: {self.holidays[trading_date]}"

        return "TRADING_DAY"

    # ---------------------------------------------------------
    # TIME
    # ---------------------------------------------------------

    def is_market_open(
        self,
        current_time=None,
        trading_date=None
    ):

        if current_time is None:
            current_time = datetime.now().time()

        if not self.is_trading_day(trading_date):
            return False

        return (
            self.MARKET_OPEN
            <= current_time
            <= self.MARKET_CLOSE
        )

    def is_entry_allowed(
        self,
        current_time=None,
        trading_date=None
    ):

        if current_time is None:
            current_time = datetime.now().time()

        if not self.is_trading_day(trading_date):
            return False

        return (
            self.MARKET_OPEN
            <= current_time
            < self.ENTRY_CUTOFF
        )

    def is_eod_time(self, current_time=None):

        if current_time is None:
            current_time = datetime.now().time()

        return current_time >= self.ENTRY_CUTOFF

    # ---------------------------------------------------------
    # NEXT / PREVIOUS MARKET DAY
    # ---------------------------------------------------------

    def next_trading_day(self, trading_date=None):

        current = self.normalize_date(trading_date)

        while True:

            current += timedelta(days=1)

            if self.is_trading_day(current):
                return current

    def previous_trading_day(self, trading_date=None):

        current = self.normalize_date(trading_date)

        while True:

            current -= timedelta(days=1)

            if self.is_trading_day(current):
                return current

    # ---------------------------------------------------------
    # INFO
    # ---------------------------------------------------------

    def describe(self, trading_date=None):

        trading_date = self.normalize_date(trading_date)

        return {
            "date": trading_date.isoformat(),
            "is_trading_day": self.is_trading_day(trading_date),
            "reason": self.get_market_day_reason(trading_date),
            "market_open": self.MARKET_OPEN.isoformat(),
            "market_close": self.MARKET_CLOSE.isoformat(),
            "entry_cutoff": self.ENTRY_CUTOFF.isoformat(),
        }
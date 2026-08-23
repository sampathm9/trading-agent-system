from datetime import datetime

from workers.calendar.market_calendar import NSEMarketCalendar


class TradingScheduler:

    def __init__(
        self,
        agent,
        market_calendar=None
    ):

        self.agent = agent

        self.market_calendar = (
            market_calendar
            or NSEMarketCalendar()
        )

        self.running = False
        self.entries_allowed = False

    # -------------------------------------------------
    # LIFECYCLE
    # -------------------------------------------------

    def start(self):

        self.running = True

        print("[SCHEDULER] Trading scheduler started")

    def stop(self):

        self.running = False
        self.entries_allowed = False

        print("[SCHEDULER] Trading scheduler stopped")

    # -------------------------------------------------
    # MARKET DAY GUARD
    # -------------------------------------------------

    def check_market_day(self):

        today = datetime.now().date()

        if not self.market_calendar.is_trading_day(today):

            reason = (
                self.market_calendar
                .get_market_day_reason(today)
            )

            print(
                f"[SCHEDULER] Market closed: {reason}"
            )

            return {
                "status": "MARKET_CLOSED",
                "date": today.isoformat(),
                "reason": reason
            }

        print("[SCHEDULER] Market day confirmed")

        return {
            "status": "TRADING_DAY",
            "date": today.isoformat(),
            "reason": "TRADING_DAY"
        }

    # -------------------------------------------------
    # PRE MARKET
    # -------------------------------------------------

    def pre_market(self):

        market_status = self.check_market_day()

        if market_status["status"] != "TRADING_DAY":

            return market_status

        print("[SCHEDULER] Pre-market phase")

        return {
            "status": "COMPLETED",
            "phase": "PRE_MARKET",
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------
    # TRADING SESSION
    # -------------------------------------------------

    def start_trading_session(self):

        market_status = self.check_market_day()

        if market_status["status"] != "TRADING_DAY":

            self.entries_allowed = False

            return market_status

        self.entries_allowed = True

        print("[SCHEDULER] Trading session started")

        return {
            "status": "COMPLETED",
            "phase": "TRADING_SESSION",
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------
    # STOP NEW ENTRIES
    # -------------------------------------------------

    def stop_new_entries(self):

        self.entries_allowed = False

        print("[SCHEDULER] New entries stopped")

        return {
            "status": "COMPLETED",
            "phase": "STOP_NEW_ENTRIES",
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------
    # EOD EXIT
    # -------------------------------------------------

    def eod_exit(self, current_prices):

        print("[SCHEDULER] EOD exit phase")

        result = self.agent.close_all_positions(
            current_prices=current_prices
        )

        return result

    # -------------------------------------------------
    # POST MARKET
    # -------------------------------------------------

    def post_market(self):

        print("[SCHEDULER] Post-market phase")

        return {
            "status": "COMPLETED",
            "phase": "POST_MARKET",
            "timestamp": datetime.now().isoformat()
        }

    # -------------------------------------------------
    # FULL DAILY CYCLE
    # -------------------------------------------------

    def run_daily_cycle(
        self,
        current_prices=None
    ):

        if not self.running:

            return {
                "status": "SCHEDULER_NOT_RUNNING"
            }

        market_status = self.check_market_day()

        if market_status["status"] != "TRADING_DAY":

            return {
                "status": "MARKET_CLOSED",
                "market": market_status,
                "pre_market": market_status,
                "trading_session": market_status,
                "stop_new_entries": market_status,
                "eod_exit": {
                    "status": "NOT_REQUIRED"
                },
                "post_market": market_status
            }

        pre_market = self.pre_market()

        trading_session = (
            self.start_trading_session()
        )

        stop_new_entries = (
            self.stop_new_entries()
        )

        eod_exit = self.eod_exit(
            current_prices or {}
        )

        post_market = self.post_market()

        return {
            "status": "COMPLETED",
            "pre_market": pre_market,
            "trading_session": trading_session,
            "stop_new_entries": stop_new_entries,
            "eod_exit": eod_exit,
            "post_market": post_market
        }
from datetime import datetime, time


class TradingSessionManager:

    PRE_MARKET_START = time(9, 0)
    MARKET_START = time(9, 15)
    FORCE_EXIT_TIME = time(15, 0)
    POST_MARKET_TIME = time(15, 30)

    def __init__(self):
        self.session_status = "SLEEPING"
        self.trading_enabled = False
        self.positions_open = False

    def get_phase(self, current_time=None):

        if current_time is None:
            current_time = datetime.now().time()

        if current_time < self.PRE_MARKET_START:
            return "SLEEP"

        if current_time < self.MARKET_START:
            return "PRE_MARKET"

        if current_time < self.FORCE_EXIT_TIME:
            return "TRADING"

        if current_time < self.POST_MARKET_TIME:
            return "POST_CLOSE"

        return "POST_MARKET"

    def start_pre_market(self):

        self.session_status = "PRE_MARKET"
        self.trading_enabled = False

        return {
            "phase": "PRE_MARKET",
            "trading_enabled": False,
            "message": "Pre-market analysis started"
        }

    def start_trading(self):

        self.session_status = "TRADING"
        self.trading_enabled = True

        return {
            "phase": "TRADING",
            "trading_enabled": True,
            "message": "Trading session started"
        }

    def force_close(self):

        self.trading_enabled = False
        self.positions_open = False
        self.session_status = "FORCE_EXIT"

        return {
            "phase": "FORCE_EXIT",
            "trading_enabled": False,
            "positions_closed": True,
            "message": "All positions must be closed"
        }

    def start_post_market(self):

        self.trading_enabled = False
        self.session_status = "POST_MARKET"

        return {
            "phase": "POST_MARKET",
            "trading_enabled": False,
            "message": "Post-market analysis started"
        }

    def sleep(self):

        self.trading_enabled = False
        self.session_status = "SLEEPING"

        return {
            "phase": "SLEEP",
            "trading_enabled": False,
            "message": "Trading agent sleeping"
        }
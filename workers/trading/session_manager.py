from enum import Enum


class TradingSession(str, Enum):

    PRE_MARKET = "PRE_MARKET"
    MARKET_OPEN = "MARKET_OPEN"
    INTRADAY = "INTRADAY"
    EOD = "EOD"
    CLOSED = "CLOSED"


class SessionManager:

    def __init__(self):
        self.session = TradingSession.PRE_MARKET

    def set_session(self, session):
        if isinstance(session, TradingSession):
            self.session = session
        else:
            self.session = TradingSession(session)

    def get_session(self):
        return self.session

    def can_trade(self):
        return self.session in {
            TradingSession.MARKET_OPEN,
            TradingSession.INTRADAY,
        }

    def is_eod(self):
        return self.session == TradingSession.EOD

    def is_closed(self):
        return self.session == TradingSession.CLOSED

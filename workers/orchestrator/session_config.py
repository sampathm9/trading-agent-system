class SessionConfig:

    def __init__(
        self,
        pre_market_start="09:00",
        market_open="09:15",
        entry_cutoff="15:00",
        market_close="15:30",
    ):

        self.pre_market_start = pre_market_start
        self.market_open = market_open
        self.entry_cutoff = entry_cutoff
        self.market_close = market_close

    def to_dict(self):

        return {
            "pre_market_start": self.pre_market_start,
            "market_open": self.market_open,
            "entry_cutoff": self.entry_cutoff,
            "market_close": self.market_close,
        }

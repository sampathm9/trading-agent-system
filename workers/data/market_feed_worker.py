from datetime import datetime

class MarketFeedWorker:

    def __init__(self):
        self.market = 'NIFTY'

    def get_snapshot(self):
        return {
            'symbol': self.market,
            'timestamp': datetime.now().isoformat(),
            'status': 'READY'
        }

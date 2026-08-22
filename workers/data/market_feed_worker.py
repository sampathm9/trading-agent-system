from datetime import datetime

class MarketFeedWorker:

    def __init__(self, symbol='NIFTY'):
        self.symbol = symbol

    def get_snapshot(self):
        return {
            'symbol': self.symbol,
            'timestamp': datetime.now().isoformat(),
            'status': 'READY'
        }

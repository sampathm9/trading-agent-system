class TrendWorker:

    def analyze(self, candles, short_period=5, long_period=10):

        closes = [float(c['close']) for c in candles]

        if len(closes) < long_period:
            return {'trend': 'UNKNOWN', 'short_average': None, 'long_average': None}

        short_average = sum(closes[-short_period:]) / short_period
        long_average = sum(closes[-long_period:]) / long_period

        if short_average > long_average:
            trend = 'BULLISH'
        elif short_average < long_average:
            trend = 'BEARISH'
        else:
            trend = 'SIDEWAYS'

        return {
            'trend': trend,
            'short_average': short_average,
            'long_average': long_average
        }

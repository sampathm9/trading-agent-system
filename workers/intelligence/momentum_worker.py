class MomentumWorker:

    def analyze(self, candles, period=5):

        closes = [float(c['close']) for c in candles]

        if len(closes) <= period:
            return {'momentum': 0.0, 'direction': 'UNKNOWN'}

        current = closes[-1]
        previous = closes[-period-1]
        momentum = current - previous

        if momentum > 0:
            direction = 'POSITIVE'
        elif momentum < 0:
            direction = 'NEGATIVE'
        else:
            direction = 'NEUTRAL'

        return {
            'momentum': momentum,
            'direction': direction
        }

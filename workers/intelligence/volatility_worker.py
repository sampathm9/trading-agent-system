class VolatilityWorker:

    def analyze(self, candles, period=10):
        closes = [float(c['close']) for c in candles]

        if len(closes) < 2:
            return {'volatility': 0.0, 'level': 'UNKNOWN'}

        changes = []
        start = max(1, len(closes) - period)

        for i in range(start, len(closes)):
            changes.append(closes[i] - closes[i - 1])

        if not changes:
            return {'volatility': 0.0, 'level': 'UNKNOWN'}

        average = sum(changes) / len(changes)
        variance = sum((x - average) ** 2 for x in changes) / len(changes)
        volatility = variance ** 0.5

        if volatility > 2:
            level = 'HIGH'
        elif volatility > 0.5:
            level = 'MEDIUM'
        else:
            level = 'LOW'

        return {
            'volatility': volatility,
            'level': level
        }

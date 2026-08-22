class ChartAnalysisWorker:

    def analyze(self, candles):

        if len(candles) < 2:
            return {
                'trend': 'UNKNOWN',
                'momentum': 0.0,
                'volatility': 0.0,
                'signal': 'WAIT'
            }

        closes = [c['close'] for c in candles]

        previous = closes[-2]
        current = closes[-1]
        momentum = current - previous

        if current > previous:
            trend = 'BULLISH'
        elif current < previous:
            trend = 'BEARISH'
        else:
            trend = 'SIDEWAYS'

        changes = []

        for i in range(1, len(closes)):
            changes.append(closes[i] - closes[i - 1])

        if changes:
            average = sum(changes) / len(changes)
            variance = sum((x - average) ** 2 for x in changes) / len(changes)
            volatility = variance ** 0.5
        else:
            volatility = 0.0

        if trend == 'BULLISH' and momentum > 0:
            signal = 'BUY_BIAS'
        elif trend == 'BEARISH' and momentum < 0:
            signal = 'SELL_BIAS'
        else:
            signal = 'WAIT'

        return {
            'trend': trend,
            'momentum': momentum,
            'volatility': volatility,
            'signal': signal
        }

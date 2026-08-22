class LevelsWorker:

    def analyze(self, candles, period=20):
        if not candles:
            return {'support': None, 'resistance': None}

        recent = candles[-period:]

        lows = [float(c['low']) for c in recent if 'low' in c]
        highs = [float(c['high']) for c in recent if 'high' in c]

        if not lows:
            lows = [float(c['close']) for c in recent]

        if not highs:
            highs = [float(c['close']) for c in recent]

        support = min(lows)
        resistance = max(highs)

        return {
            'support': support,
            'resistance': resistance
        }

class RegimeWorker:

    def analyze(self, trend, volatility):

        if trend == 'UNKNOWN' or volatility == 'UNKNOWN':
            return {'regime': 'UNKNOWN'}

        if trend in ('BULLISH', 'BEARISH') and volatility == 'HIGH':
            regime = 'TRENDING_VOLATILE'
        elif trend in ('BULLISH', 'BEARISH'):
            regime = 'TRENDING'
        elif volatility == 'HIGH':
            regime = 'VOLATILE_RANGE'
        else:
            regime = 'RANGE'

        return {'regime': regime}

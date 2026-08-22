class CandleBuilderWorker:

    def build(self, raw_data):
        candles = []

        for item in raw_data:
            candles.append({
                'timestamp': item['timestamp'],
                'open': float(item['open']),
                'high': float(item['high']),
                'low': float(item['low']),
                'close': float(item['close']),
                'volume': int(item.get('volume', 0))
            })

        return candles

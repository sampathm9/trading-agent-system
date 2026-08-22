class MarketIntelligenceWorker:

    def analyze(self, candles, market_text=""):

        if not candles:
            return {
                "market_bias": "UNKNOWN",
                "evidence_score": 0.0,
                "reason": "No market data"
            }

        closes = [
            float(candle["close"])
            for candle in candles
        ]

        if len(closes) < 2:
            return {
                "market_bias": "NEUTRAL",
                "evidence_score": 0.0,
                "reason": "Not enough candles"
            }

        first_close = closes[0]
        last_close = closes[-1]

        change = last_close - first_close

        if change > 0:
            bias = "BULLISH"
        elif change < 0:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        evidence_score = abs(change) / first_close

        return {
            "market_bias": bias,
            "evidence_score": round(
                evidence_score,
                4
            ),
            "first_close": first_close,
            "last_close": last_close,
            "price_change": round(
                change,
                2
            ),
            "market_text": market_text
        }
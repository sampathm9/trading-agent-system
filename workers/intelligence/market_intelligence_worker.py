class MarketIntelligenceWorker:

    def analyze(self, candles, market_text=""):

        if not candles:
            return {
                "market_bias": "UNKNOWN",
                "trend": "UNKNOWN",
                "momentum": 0,
                "evidence_score": 0,
                "reason": "No candle data"
            }

        closes = [float(candle["close"]) for candle in candles]

        first_close = closes[0]
        last_close = closes[-1]

        if last_close > first_close:
            trend = "BULLISH"
        elif last_close < first_close:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"

        if len(closes) >= 2:
            momentum = last_close - closes[-2]
        else:
            momentum = 0

        evidence_score = 0

        if trend == "BULLISH":
            evidence_score += 1

        if trend == "BEARISH":
            evidence_score += 1

        if momentum > 0:
            evidence_score += 1

        elif momentum < 0:
            evidence_score += 1

        if trend == "BULLISH":
            market_bias = "BULLISH"

        elif trend == "BEARISH":
            market_bias = "BEARISH"

        else:
            market_bias = "NEUTRAL"

        return {
            "market_bias": market_bias,
            "trend": trend,
            "momentum": momentum,
            "evidence_score": evidence_score,
            "last_price": last_close,
            "market_text": market_text,
            "reason": (
                f"Price moved from {first_close} "
                f"to {last_close}"
            )
        }
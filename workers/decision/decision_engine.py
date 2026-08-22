class DecisionEngine:

    def decide(self, analysis, selected_strategy=None):

        if not analysis:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "No analysis available"
            }

        bias = analysis.get(
            "market_bias",
            "UNKNOWN"
        )

        evidence = float(
            analysis.get(
                "evidence_score",
                0
            )
        )

        strategy = selected_strategy

        if strategy is None:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "No strategy selected"
            }

        if bias == "BULLISH":

            return {
                "action": "BUY",
                "confidence": min(
                    1.0,
                    strategy.get(
                        "confidence",
                        evidence
                    )
                ),
                "reason": "Bullish market bias"
            }

        if bias == "BEARISH":

            return {
                "action": "SELL",
                "confidence": min(
                    1.0,
                    strategy.get(
                        "confidence",
                        evidence
                    )
                ),
                "reason": "Bearish market bias"
            }

        return {
            "action": "HOLD",
            "confidence": 0.0,
            "reason": "Neutral market"
        }
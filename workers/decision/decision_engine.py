class DecisionEngine:

    def decide(self, market_analysis, strategy_result):

        if strategy_result is None:
            return {
                'action': 'WAIT',
                'confidence': 0.0,
                'reason': 'No validated strategy available'
            }

        bias = market_analysis.get('market_bias', 'NEUTRAL')
        evidence_score = market_analysis.get('evidence_score', 0)

        win_rate = strategy_result.get('win_rate', 0.0)
        total_pnl = strategy_result.get('total_pnl', 0.0)

        confidence = min(100.0, max(0.0,
            50.0 +
            evidence_score * 10.0 +
            (win_rate - 50.0) * 0.5
        ))

        if bias == 'BULLISH' and evidence_score >= 3:
            action = 'BUY'
            reason = 'Bullish market evidence supports the validated strategy'
        elif bias == 'BEARISH' and evidence_score <= -3:
            action = 'SELL'
            reason = 'Bearish market evidence supports the validated strategy'
        else:
            action = 'WAIT'
            reason = 'Market evidence is not strong enough'

        return {
            'action': action,
            'confidence': confidence,
            'reason': reason,
            'strategy_pnl': total_pnl,
            'strategy_win_rate': win_rate
        }

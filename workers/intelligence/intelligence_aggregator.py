from workers.intelligence.chart_analysis_worker import ChartAnalysisWorker
from workers.intelligence.trend_worker import TrendWorker
from workers.intelligence.momentum_worker import MomentumWorker
from workers.intelligence.volatility_worker import VolatilityWorker
from workers.intelligence.levels_worker import LevelsWorker
from workers.intelligence.regime_worker import RegimeWorker
from workers.intelligence.sentiment_worker import SentimentWorker

class IntelligenceAggregator:

    def __init__(self):
        self.chart = ChartAnalysisWorker()
        self.trend = TrendWorker()
        self.momentum = MomentumWorker()
        self.volatility = VolatilityWorker()
        self.levels = LevelsWorker()
        self.regime = RegimeWorker()
        self.sentiment = SentimentWorker()

    def analyze(self, candles, market_text=''):

        chart_result = self.chart.analyze(candles)
        trend_result = self.trend.analyze(candles)
        momentum_result = self.momentum.analyze(candles)
        volatility_result = self.volatility.analyze(candles)
        levels_result = self.levels.analyze(candles)
        sentiment_result = self.sentiment.analyze(market_text)

        regime_result = self.regime.analyze(
            trend_result['trend'],
            volatility_result['level']
        )

        evidence = 0

        if chart_result['signal'] == 'BUY_BIAS':
            evidence += 1
        elif chart_result['signal'] == 'SELL_BIAS':
            evidence -= 1

        if trend_result['trend'] == 'BULLISH':
            evidence += 1
        elif trend_result['trend'] == 'BEARISH':
            evidence -= 1

        if momentum_result['direction'] == 'POSITIVE':
            evidence += 1
        elif momentum_result['direction'] == 'NEGATIVE':
            evidence -= 1

        if sentiment_result['sentiment'] == 'POSITIVE':
            evidence += 1
        elif sentiment_result['sentiment'] == 'NEGATIVE':
            evidence -= 1

        if evidence >= 3:
            bias = 'BULLISH'
        elif evidence <= -3:
            bias = 'BEARISH'
        else:
            bias = 'NEUTRAL'

        return {
            'chart': chart_result,
            'trend': trend_result,
            'momentum': momentum_result,
            'volatility': volatility_result,
            'levels': levels_result,
            'sentiment': sentiment_result,
            'regime': regime_result,
            'evidence_score': evidence,
            'market_bias': bias
        }

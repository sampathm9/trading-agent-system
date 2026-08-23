from workers.strategy.strategy_worker import StrategyWorker


class DecisionWorker:

    def __init__(self, strategy_worker=None):
        self.strategy_worker = strategy_worker or StrategyWorker()

    def decide(self, trend):

        action = self.strategy_worker.decide(trend)

        return {
            "trend": trend,
            "action": action,
            "confidence": 1.0 if action in ("BUY", "SELL") else 0.0
        }
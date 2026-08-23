from workers.intelligence.trend_worker import TrendWorker
from workers.decision.decision_worker import DecisionWorker
from workers.execution.execution_worker import ExecutionWorker


class TradingCycleWorker:

    def __init__(
        self,
        trend_worker=None,
        decision_worker=None,
        execution_worker=None
    ):
        self.trend_worker = trend_worker or TrendWorker()
        self.decision_worker = decision_worker or DecisionWorker()
        self.execution_worker = execution_worker or ExecutionWorker()

    def run(
        self,
        candles,
        symbol,
        quantity,
        price,
        short_period=5,
        long_period=10,
        daily_loss=0.0
    ):

        trend_result = self.trend_worker.analyze(
            candles,
            short_period=short_period,
            long_period=long_period
        )

        trend = trend_result["trend"]

        decision = self.decision_worker.decide(trend)

        execution = self.execution_worker.execute(
            decision=decision,
            symbol=symbol,
            quantity=quantity,
            price=price,
            daily_loss=daily_loss
        )

        return {
            "trend": trend_result,
            "decision": decision,
            "execution": execution
        }
from workers.intelligence.trend_worker import TrendWorker
from workers.decision.decision_worker import DecisionWorker
from workers.execution.execution_worker import ExecutionWorker


_POSITION_NOT_PROVIDED = object()


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
        daily_loss=0.0,
        position=_POSITION_NOT_PROVIDED
    ):

        trend_result = self.trend_worker.analyze(
            candles,
            short_period=short_period,
            long_period=long_period
        )

        trend = trend_result["trend"]

        decision = self.decision_worker.decide(trend)

        if position is not _POSITION_NOT_PROVIDED:

            action = decision.get("action")

            if position is not None and action == "BUY":
                decision = {
                    **decision,
                    "action": "HOLD",
                    "reason": "POSITION_ALREADY_OPEN"
                }

            elif position is None and action == "SELL":
                decision = {
                    **decision,
                    "action": "HOLD",
                    "reason": "NO_OPEN_POSITION"
                }

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
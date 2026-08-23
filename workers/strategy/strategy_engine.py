from workers.strategy.strategy_config import (
    StrategyConfig
)

from workers.strategy.trend_strategy import (
    TrendStrategy
)

from workers.signals.signal_worker import (
    SignalWorker
)


class StrategyEngine:

    def __init__(
        self,
        config=None,
        trend_strategy=None,
        signal_worker=None,
    ):

        self.config = (
            config
            or StrategyConfig()
        )

        self.trend_strategy = (
            trend_strategy
            or TrendStrategy()
        )

        self.signal_worker = (
            signal_worker
            or SignalWorker(
                minimum_confidence=(
                    self.config.minimum_confidence
                )
            )
        )

    def analyze(
        self,
        candles
    ):

        trend = self.trend_strategy.analyze(
            candles=candles,
            short_period=(
                self.config.short_period
            ),
            long_period=(
                self.config.long_period
            ),
            momentum_period=(
                self.config.momentum_period
            ),
        )

        signal = self.signal_worker.generate(
            trend
        )

        return {
            "status": "COMPLETED",
            "trend": trend,
            "signal": signal,
            "config": self.config.to_dict(),
        }

    def get_last_signal(self):

        return self.signal_worker.get_last_signal()

    def get_signal_history(self):

        return self.signal_worker.get_signal_history()
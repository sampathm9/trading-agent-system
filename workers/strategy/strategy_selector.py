class StrategySelector:

    def __init__(
        self,
        minimum_win_rate=0.50,
        minimum_trades=10
    ):
        self.minimum_win_rate = minimum_win_rate
        self.minimum_trades = minimum_trades

    def select(self, backtest_results):

        if not backtest_results:
            return None

        valid_strategies = []

        for strategy in backtest_results:

            win_rate = float(
                strategy.get("win_rate", 0)
            )

            trades = int(
                strategy.get("trades", 0)
            )

            if (
                win_rate >= self.minimum_win_rate
                and trades >= self.minimum_trades
            ):
                valid_strategies.append(strategy)

        if not valid_strategies:
            return None

        selected = max(
            valid_strategies,
            key=lambda x: x.get("score", 0)
        )

        return selected
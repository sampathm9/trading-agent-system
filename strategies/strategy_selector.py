class StrategySelector:

    def __init__(self, min_trades=5, min_win_rate=50.0):
        self.min_trades = min_trades
        self.min_win_rate = min_win_rate

    def select(self, results):
        eligible = []

        for result in results:
            if result.get('total_trades', 0) < self.min_trades:
                continue

            if result.get('win_rate', 0.0) < self.min_win_rate:
                continue

            eligible.append(result)

        if not eligible:
            return None

        eligible.sort(
            key=lambda x: (
                x.get('total_pnl', 0.0),
                x.get('win_rate', 0.0)
            ),
            reverse=True
        )

        return eligible[0]

from workers.trading.trading_cycle_worker import TradingCycleWorker


class BacktestEngine:

    def __init__(self, trading_cycle=None):
        self.trading_cycle = trading_cycle or TradingCycleWorker()

    def run(
        self,
        candles,
        symbol,
        quantity=1,
        short_period=5,
        long_period=10
    ):

        results = []

        for index in range(len(candles)):

            current_candles = candles[:index + 1]

            price = current_candles[-1]["close"]

            result = self.trading_cycle.run(
                candles=current_candles,
                symbol=symbol,
                quantity=quantity,
                price=price,
                short_period=short_period,
                long_period=long_period
            )

            results.append({
                "index": index,
                "price": price,
                "result": result
            })

        return results
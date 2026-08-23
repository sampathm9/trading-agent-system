from workers.data.market_data_worker import MarketDataWorker
from workers.trading.trading_cycle_worker import TradingCycleWorker
from workers.backtest.backtest_worker import BacktestWorker


class DailyTradingAgent:

    def __init__(
        self,
        market_data_worker=None,
        trading_cycle_worker=None,
        backtest_worker=None
    ):

        self.market_data_worker = (
            market_data_worker
            or MarketDataWorker()
        )

        self.trading_cycle_worker = (
            trading_cycle_worker
            or TradingCycleWorker()
        )

        self.backtest_worker = (
            backtest_worker
            or BacktestWorker()
        )

        self.running = False

    def load_market_data(self, symbol, candles):

        data = self.market_data_worker.load_candles(
            symbol,
            candles
        )

        return data

    def get_latest_price(self, symbol):

        return self.market_data_worker.latest_price(
            symbol
        )

    def run_trading_cycle(
        self,
        symbol,
        quantity=1,
        short_period=5,
        long_period=10,
        daily_loss=0.0
    ):

        candles = self.market_data_worker.get_candles(
            symbol
        )

        if not candles:
            return {
                "status": "NO_DATA",
                "reason": "NO_MARKET_DATA"
            }

        price = self.market_data_worker.latest_price(
            symbol
        )

        result = self.trading_cycle_worker.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            price=price,
            short_period=short_period,
            long_period=long_period,
            daily_loss=daily_loss
        )

        return result

    def run_backtest(
        self,
        symbol,
        quantity=1,
        short_period=5,
        long_period=10,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=None
    ):

        candles = self.market_data_worker.get_candles(
            symbol
        )

        if not candles:
            return {
                "status": "NO_DATA",
                "reason": "NO_MARKET_DATA"
            }

        result = self.backtest_worker.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            short_period=short_period,
            long_period=long_period,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            max_daily_loss=max_daily_loss
        )

        return result

    def start(self):

        self.running = True

        print("[DAILY AGENT] Trading agent started")

    def stop(self):

        self.running = False

        print("[DAILY AGENT] Trading agent stopped")
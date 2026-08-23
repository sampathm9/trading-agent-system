from workers.data.market_data_worker import MarketDataWorker
from workers.trading.trading_cycle_worker import TradingCycleWorker
from workers.backtest.backtest_worker import BacktestWorker
from workers.execution.execution_worker import ExecutionWorker


class DailyTradingAgent:

    def __init__(
        self,
        market_data_worker=None,
        trading_cycle_worker=None,
        backtest_worker=None,
        execution_worker=None
    ):

        self.market_data_worker = (
            market_data_worker
            or MarketDataWorker()
        )

        self.execution_worker = (
            execution_worker
            or ExecutionWorker()
        )

        self.trading_cycle_worker = (
            trading_cycle_worker
            or TradingCycleWorker(
                execution_worker=self.execution_worker
            )
        )

        self.backtest_worker = (
            backtest_worker
            or BacktestWorker()
        )

        self.running = False

    # -------------------------------------------------
    # MARKET DATA
    # -------------------------------------------------

    def load_market_data(self, symbol, candles):

        return self.market_data_worker.load_candles(
            symbol,
            candles
        )

    def get_latest_price(self, symbol):

        return self.market_data_worker.latest_price(
            symbol
        )

    # -------------------------------------------------
    # POSITION
    # -------------------------------------------------

    def get_position(self, symbol):

        return self.execution_worker.broker.get_position(
            symbol
        )

    def get_realized_pnl(self):

        return self.execution_worker.broker.get_realized_pnl()

    # -------------------------------------------------
    # TRADING CYCLE
    # -------------------------------------------------

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

        position = self.get_position(symbol)

        result = self.trading_cycle_worker.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            price=price,
            short_period=short_period,
            long_period=long_period,
            daily_loss=daily_loss,
            position=position
        )

        return result

    # -------------------------------------------------
    # EOD EXIT
    # -------------------------------------------------

        # -------------------------------------------------
    # EOD EXIT
    # -------------------------------------------------

    def close_all_positions(self, current_prices):

        print()
        print("[DAILY AGENT] EOD position exit")

        closing_orders = (
            self.execution_worker.broker.close_all_positions(
                current_prices=current_prices
            )
        )

        return {
            "status": "COMPLETED",
            "closing_orders": closing_orders,
            "realized_pnl": (
                self.execution_worker.broker.get_realized_pnl()
            )
        }

    def run_eod_exit(self, current_prices=None):

        if current_prices is None:
            current_prices = {}

        return self.close_all_positions(
            current_prices=current_prices
        )
    # -------------------------------------------------
    # BACKTEST
    # -------------------------------------------------

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

        return self.backtest_worker.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            short_period=short_period,
            long_period=long_period,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            max_daily_loss=max_daily_loss
        )

    # -------------------------------------------------
    # LIFECYCLE
    # -------------------------------------------------

    def start(self):

        self.running = True

        print("[DAILY AGENT] Trading agent started")

    def stop(self):

        self.running = False

        print("[DAILY AGENT] Trading agent stopped")
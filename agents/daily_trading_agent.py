from datetime import date

from workers.data.market_data_worker import MarketDataWorker
from workers.trading.trading_cycle_worker import TradingCycleWorker
from workers.backtest.backtest_worker import BacktestWorker
from workers.execution.execution_worker import ExecutionWorker
from workers.calendar.market_calendar import NSEMarketCalendar


class DailyTradingAgent:

    def __init__(
        self,
        market_data_worker=None,
        trading_cycle_worker=None,
        backtest_worker=None,
        execution_worker=None,
        market_calendar=None,
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

        self.market_calendar = (
            market_calendar
            or NSEMarketCalendar()
        )

        self.running = False
        self.current_date = None

    # -------------------------------------------------
    # MARKET DATE
    # -------------------------------------------------

    def set_trading_date(self, trading_date=None):

        if trading_date is None:
            trading_date = date.today()

        self.current_date = trading_date

        return self.current_date

    def is_market_day(self):

        trading_date = (
            self.current_date
            or date.today()
        )

        return self.market_calendar.is_trading_day(
            trading_date
        )

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
        daily_loss=0.0,
    ):

        if not self.is_market_day():

            trading_date = (
                self.current_date
                or date.today()
            )

            reason = self.market_calendar.get_market_day_reason(
                trading_date
            )

            print(
                f"[DAILY AGENT] Market closed: {reason}"
            )

            return {
                "status": "SKIPPED",
                "reason": reason,
                "date": str(trading_date),
            }

        candles = self.market_data_worker.get_candles(
            symbol
        )

        if not candles:

            return {
                "status": "NO_DATA",
                "reason": "NO_MARKET_DATA",
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
            position=position,
        )

        return result

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
            ),
        }

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
        max_daily_loss=None,
    ):

        candles = self.market_data_worker.get_candles(
            symbol
        )

        if not candles:

            return {
                "status": "NO_DATA",
                "reason": "NO_MARKET_DATA",
            }

        return self.backtest_worker.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            short_period=short_period,
            long_period=long_period,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            max_daily_loss=max_daily_loss,
        )

    # -------------------------------------------------
    # LIFECYCLE
    # -------------------------------------------------

    def start(self, trading_date=None):

        self.set_trading_date(
            trading_date
        )

        if not self.is_market_day():

            reason = self.market_calendar.get_market_day_reason(
                self.current_date
            )

            self.running = False

            print(
                f"[DAILY AGENT] Market closed: {reason}"
            )

            return {
                "status": "MARKET_CLOSED",
                "date": str(self.current_date),
                "reason": reason,
            }

        self.running = True

        print(
            "[DAILY AGENT] Trading agent started"
        )

        return {
            "status": "STARTED",
            "date": str(self.current_date),
        }

    def stop(self):

        self.running = False

        print(
            "[DAILY AGENT] Trading agent stopped"
        )
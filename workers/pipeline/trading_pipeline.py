from datetime import datetime, date

from workers.calendar.market_calendar import NSEMarketCalendar


class TradingPipeline:

    def __init__(
        self,
        runtime,
        market_data_worker,
        strategy_engine,
        market_calendar=None,
        symbol="NIFTY",
    ):
        self.runtime = runtime
        self.market_data_worker = market_data_worker
        self.strategy_engine = strategy_engine
        self.calendar = market_calendar or NSEMarketCalendar()
        self.symbol = symbol

        self.events = []
        self.running = False

    def log_event(self, event, **details):

        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **details,
        }

        self.events.append(record)

        print(
            f"[PIPELINE] {event}"
        )

        return record

    # ---------------------------------------------------------
    # MARKET DAY
    # ---------------------------------------------------------

    def start(self, trading_date=None):

        if trading_date is None:
            trading_date = date.today()

        if not self.calendar.is_trading_day(
            trading_date
        ):

            reason = (
                self.calendar.get_market_day_reason(
                    trading_date
                )
            )

            self.log_event(
                "MARKET_CLOSED",
                date=str(trading_date),
                reason=reason,
            )

            self.running = False

            return {
                "status": "MARKET_CLOSED",
                "date": str(trading_date),
                "reason": reason,
            }

        result = self.runtime.start(
            trading_date
        )

        if result.get("status") == "STARTED":

            self.running = True

            self.log_event(
                "PIPELINE_STARTED",
                date=str(trading_date),
            )

        return result

    # ---------------------------------------------------------
    # MARKET DATA
    # ---------------------------------------------------------

    def get_candles(self, limit=100):

        candles = (
            self.market_data_worker.get_candles(
                self.symbol
            )
        )

        if limit is not None:
            candles = candles[-limit:]

        return candles

    # ---------------------------------------------------------
    # STRATEGY
    # ---------------------------------------------------------

    def run_strategy(self, candles):

        result = self.strategy_engine.analyze(
            candles
        )

        self.log_event(
            "STRATEGY_COMPLETED",
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # ENTRY
    # ---------------------------------------------------------

    def run_entry(self):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        if not self.runtime.entries_enabled:

            return {
                "status": "ENTRIES_DISABLED"
            }

        if self.runtime.daily_loss_limit_reached():

            return {
                "status": "DAILY_LOSS_LIMIT"
            }

        result = self.runtime.run_entry_cycle()

        self.log_event(
            "ENTRY_CYCLE",
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # POSITION MONITOR
    # ---------------------------------------------------------

    def monitor(self, current_price):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        result = self.runtime.monitor_position(
            current_price
        )

        self.log_event(
            "POSITION_MONITOR",
            price=current_price,
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # STOP NEW ENTRIES
    # ---------------------------------------------------------

    def stop_new_entries(self):

        result = (
            self.runtime.stop_new_entries()
        )

        self.log_event(
            "NEW_ENTRIES_STOPPED",
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # EOD
    # ---------------------------------------------------------

    def eod_exit(self, current_price):

        result = self.runtime.eod_exit(
            current_price
        )

        self.log_event(
            "EOD_EXIT",
            price=current_price,
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------

    def stop(self):

        result = self.runtime.stop()

        self.running = False

        self.log_event(
            "PIPELINE_STOPPED"
        )

        return result

    # ---------------------------------------------------------
    # FULL SESSION
    # ---------------------------------------------------------

    def run_session(
        self,
        trading_date=None,
        monitor_prices=None,
        eod_price=None,
    ):

        if monitor_prices is None:
            monitor_prices = []

        start_result = self.start(
            trading_date
        )

        if start_result.get("status") != "STARTED":

            return {
                "status": start_result.get(
                    "status"
                ),
                "start": start_result,
            }

        candles = self.get_candles()

        strategy_result = (
            self.run_strategy(
                candles
            )
        )

        entry_result = self.run_entry()

        monitor_results = []

        for price in monitor_prices:

            monitor_result = self.monitor(
                price
            )

            monitor_results.append(
                monitor_result
            )

            if (
                self.runtime.get_position()
                is None
            ):
                break

        stop_entries_result = (
            self.stop_new_entries()
        )

        eod_result = None

        if eod_price is not None:

            eod_result = self.eod_exit(
                eod_price
            )

        final_state = (
            self.runtime.get_state()
        )

        self.stop()

        return {
            "status": "COMPLETED",
            "start": start_result,
            "strategy": strategy_result,
            "entry": entry_result,
            "monitor": monitor_results,
            "stop_new_entries": (
                stop_entries_result
            ),
            "eod": eod_result,
            "final_state": final_state,
        }

    # ---------------------------------------------------------
    # STATE
    # ---------------------------------------------------------

    def get_state(self):

        return {
            "running": self.running,
            "symbol": self.symbol,
            "event_count": len(
                self.events
            ),
            "runtime": (
                self.runtime.get_state()
            ),
        }

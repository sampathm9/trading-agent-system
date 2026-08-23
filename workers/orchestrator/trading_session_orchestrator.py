from datetime import datetime, date, time

from workers.calendar.market_calendar import NSEMarketCalendar
from workers.orchestrator.session_config import SessionConfig


class TradingSessionOrchestrator:

    PRE_MARKET = "PRE_MARKET"
    MARKET_OPEN = "MARKET_OPEN"
    TRADING = "TRADING"
    ENTRY_CUTOFF = "ENTRY_CUTOFF"
    MARKET_CLOSE = "MARKET_CLOSE"
    CLOSED = "CLOSED"

    def __init__(
        self,
        pipeline,
        market_calendar=None,
        config=None,
        symbol="NIFTY",
    ):

        self.pipeline = pipeline

        self.calendar = (
            market_calendar
            or NSEMarketCalendar()
        )

        self.config = (
            config
            or SessionConfig()
        )

        self.symbol = symbol

        self.current_date = None
        self.phase = self.CLOSED
        self.running = False

        self.events = []

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def log_event(self, event, **details):

        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "phase": self.phase,
            **details,
        }

        self.events.append(record)

        print(
            f"[ORCHESTRATOR] {event}"
        )

        return record

    # ---------------------------------------------------------
    # MARKET DAY
    # ---------------------------------------------------------

    def is_trading_day(self, trading_date):

        return self.calendar.is_trading_day(
            trading_date
        )

    # ---------------------------------------------------------
    # START
    # ---------------------------------------------------------

    def start(self, trading_date=None):

        if trading_date is None:
            trading_date = date.today()

        if not self.is_trading_day(
            trading_date
        ):

            reason = (
                self.calendar.get_market_day_reason(
                    trading_date
                )
            )

            self.phase = self.CLOSED
            self.running = False
            self.current_date = trading_date

            self.log_event(
                "MARKET_CLOSED",
                date=str(trading_date),
                reason=reason,
            )

            return {
                "status": "MARKET_CLOSED",
                "date": str(trading_date),
                "reason": reason,
            }

        self.current_date = trading_date
        self.running = True
        self.phase = self.PRE_MARKET

        self.log_event(
            "SESSION_STARTED",
            date=str(trading_date),
        )

        pipeline_result = self.pipeline.start(
            trading_date
        )

        if pipeline_result.get(
            "status"
        ) != "STARTED":

            self.running = False
            self.phase = self.CLOSED

            return {
                "status": "FAILED",
                "pipeline": pipeline_result,
            }

        return {
            "status": "STARTED",
            "date": str(trading_date),
            "phase": self.phase,
        }

    # ---------------------------------------------------------
    # PHASE CONTROL
    # ---------------------------------------------------------

    def set_phase(self, phase):

        if phase not in {
            self.PRE_MARKET,
            self.MARKET_OPEN,
            self.TRADING,
            self.ENTRY_CUTOFF,
            self.MARKET_CLOSE,
            self.CLOSED,
        }:

            raise ValueError(
                f"Invalid session phase: {phase}"
            )

        self.phase = phase

        self.log_event(
            "PHASE_CHANGED",
            new_phase=phase,
        )

        return {
            "status": "COMPLETED",
            "phase": phase,
        }

    # ---------------------------------------------------------
    # MARKET OPEN
    # ---------------------------------------------------------

    def open_market(self):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        return self.set_phase(
            self.MARKET_OPEN
        )

    # ---------------------------------------------------------
    # ENABLE TRADING
    # ---------------------------------------------------------

    def enable_trading(self):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        result = self.set_phase(
            self.TRADING
        )

        self.pipeline.runtime.entries_enabled = True

        self.log_event(
            "TRADING_ENABLED"
        )

        return result

    # ---------------------------------------------------------
    # MARKET DATA
    # ---------------------------------------------------------

    def get_market_data(self, limit=100):

        if not self.running:

            return {
                "status": "STOPPED",
                "candles": [],
            }

        candles = self.pipeline.get_candles(
            limit=limit
        )

        self.log_event(
            "MARKET_DATA_LOADED",
            candles=len(candles),
        )

        return {
            "status": "COMPLETED",
            "candles": candles,
            "count": len(candles),
        }

    # ---------------------------------------------------------
    # STRATEGY
    # ---------------------------------------------------------

    def run_strategy(self, candles):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        result = self.pipeline.run_strategy(
            candles
        )

        self.log_event(
            "STRATEGY_EXECUTED",
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

        if self.phase != self.TRADING:

            return {
                "status": "ENTRY_NOT_ALLOWED",
                "phase": self.phase,
            }

        result = self.pipeline.run_entry()

        self.log_event(
            "ENTRY_EXECUTED",
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # POSITION MONITOR
    # ---------------------------------------------------------

    def monitor_position(self, price):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        result = self.pipeline.monitor(
            price
        )

        self.log_event(
            "POSITION_MONITORED",
            price=price,
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # ENTRY CUTOFF
    # ---------------------------------------------------------

    def stop_entries(self):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        result = self.set_phase(
            self.ENTRY_CUTOFF
        )

        self.pipeline.stop_new_entries()

        self.log_event(
            "ENTRY_CUTOFF_REACHED"
        )

        return result

    # ---------------------------------------------------------
    # EOD
    # ---------------------------------------------------------

    def eod_exit(self, price):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        self.set_phase(
            self.MARKET_CLOSE
        )

        result = self.pipeline.eod_exit(
            price
        )

        self.log_event(
            "EOD_EXIT_COMPLETED",
            price=price,
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------

    def stop(self):

        if not self.running:

            return {
                "status": "ALREADY_STOPPED"
            }

        result = self.pipeline.stop()

        self.running = False
        self.phase = self.CLOSED

        self.log_event(
            "SESSION_STOPPED"
        )

        return {
            "status": "STOPPED",
            "pipeline": result,
        }

    # ---------------------------------------------------------
    # FULL SIMULATED SESSION
    # ---------------------------------------------------------

    def run_session(
        self,
        trading_date,
        monitor_prices=None,
        eod_price=None,
    ):

        if monitor_prices is None:
            monitor_prices = []

        start = self.start(
            trading_date
        )

        if start.get("status") != "STARTED":

            return {
                "status": start.get(
                    "status"
                ),
                "start": start,
            }

        self.open_market()

        self.enable_trading()

        market_data = self.get_market_data()

        strategy = self.run_strategy(
            market_data["candles"]
        )

        entry = self.run_entry()

        monitor = []

        for price in monitor_prices:

            result = self.monitor_position(
                price
            )

            monitor.append(result)

            if (
                self.pipeline.runtime.get_position()
                is None
            ):
                break

        cutoff = self.stop_entries()

        eod = None

        if eod_price is not None:

            eod = self.eod_exit(
                eod_price
            )

        state = self.get_state()

        self.stop()

        return {
            "status": "COMPLETED",
            "start": start,
            "market_data": {
                "count": market_data["count"]
            },
            "strategy": strategy,
            "entry": entry,
            "monitor": monitor,
            "cutoff": cutoff,
            "eod": eod,
            "state": state,
        }

    # ---------------------------------------------------------
    # STATE
    # ---------------------------------------------------------

    def get_state(self):

        return {
            "running": self.running,
            "date": (
                str(self.current_date)
                if self.current_date
                else None
            ),
            "phase": self.phase,
            "symbol": self.symbol,
            "event_count": len(
                self.events
            ),
            "pipeline": (
                self.pipeline.get_state()
            ),
        }

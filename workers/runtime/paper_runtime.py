from datetime import date, datetime

from workers.calendar.market_calendar import NSEMarketCalendar


class PaperTradingRuntime:

    def __init__(
        self,
        agent,
        market_calendar=None,
        symbol="NIFTY",
        quantity=1,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000.0,
    ):
        self.agent = agent
        self.calendar = market_calendar or NSEMarketCalendar()

        self.symbol = symbol
        self.quantity = quantity

        self.stop_loss_pct = float(stop_loss_pct)
        self.take_profit_pct = float(take_profit_pct)
        self.max_daily_loss = float(max_daily_loss)

        self.running = False
        self.entries_enabled = False
        self.current_date = None

        self.events = []
        self.trade_count = 0

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def log_event(self, event, **details):
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **details,
        }

        self.events.append(record)

        print(f"[RUNTIME] {event}")

        return record

    # ---------------------------------------------------------
    # MARKET DAY
    # ---------------------------------------------------------

    def check_market_day(self, trading_date=None):

        if trading_date is None:
            trading_date = date.today()

        if isinstance(trading_date, datetime):
            trading_date = trading_date.date()

        allowed = self.calendar.is_trading_day(trading_date)

        if not allowed:

            reason = self.calendar.get_market_day_reason(
                trading_date
            )

            self.log_event(
                "MARKET_CLOSED",
                date=str(trading_date),
                reason=reason,
            )

            return False

        self.log_event(
            "MARKET_DAY",
            date=str(trading_date),
        )

        return True

    # ---------------------------------------------------------
    # START / STOP
    # ---------------------------------------------------------

    def start(self, trading_date=None):

        if trading_date is None:
            trading_date = date.today()

        if isinstance(trading_date, datetime):
            trading_date = trading_date.date()

        if not self.check_market_day(trading_date):

            self.running = False
            self.entries_enabled = False

            return {
                "status": "MARKET_CLOSED",
                "date": str(trading_date),
            }

        self.current_date = trading_date

        agent_result = self.agent.start(
            trading_date=trading_date
        )

        if agent_result.get("status") != "STARTED":

            self.running = False
            self.entries_enabled = False

            return agent_result

        self.running = True
        self.entries_enabled = True

        self.log_event(
            "RUNTIME_STARTED",
            date=str(trading_date),
        )

        return {
            "status": "STARTED",
            "date": str(trading_date),
        }

    def stop(self):

        self.running = False
        self.entries_enabled = False

        if self.agent.running:
            self.agent.stop()

        self.log_event(
            "RUNTIME_STOPPED"
        )

        return {
            "status": "STOPPED"
        }

    # ---------------------------------------------------------
    # DAILY LOSS
    # ---------------------------------------------------------

    def get_daily_loss(self):

        realized_pnl = self.agent.get_realized_pnl()

        if realized_pnl >= 0:
            return 0.0

        return abs(realized_pnl)

    def daily_loss_limit_reached(self):

        loss = self.get_daily_loss()

        if loss >= self.max_daily_loss:

            self.entries_enabled = False

            self.log_event(
                "DAILY_LOSS_LIMIT_REACHED",
                daily_loss=loss,
                max_daily_loss=self.max_daily_loss,
            )

            return True

        return False

    # ---------------------------------------------------------
    # POSITION
    # ---------------------------------------------------------

    def get_position(self):

        return self.agent.get_position(
            self.symbol
        )

    # ---------------------------------------------------------
    # ENTRY
    # ---------------------------------------------------------

    def run_entry_cycle(
        self,
        short_period=5,
        long_period=10,
    ):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        if not self.entries_enabled:

            return {
                "status": "ENTRIES_DISABLED"
            }

        if not self.is_market_day():

            return {
                "status": "SKIPPED",
                "reason": "MARKET_CLOSED",
            }

        if self.daily_loss_limit_reached():

            return {
                "status": "DAILY_LOSS_LIMIT"
            }

        position = self.get_position()

        if position is not None:

            return {
                "status": "POSITION_ALREADY_OPEN",
                "position": position,
            }

        result = self.agent.run_trading_cycle(
            symbol=self.symbol,
            quantity=self.quantity,
            short_period=short_period,
            long_period=long_period,
            daily_loss=self.get_daily_loss(),
        )

        if result.get("status") == "EXECUTED":

            self.trade_count += 1

            self.log_event(
                "ENTRY_EXECUTED",
                result=result,
            )

        return result

    # ---------------------------------------------------------
    # MARKET DAY CHECK
    # ---------------------------------------------------------

    def is_market_day(self):

        trading_date = (
            self.current_date
            or date.today()
        )

        return self.calendar.is_trading_day(
            trading_date
        )

    # ---------------------------------------------------------
    # POSITION MONITOR
    # ---------------------------------------------------------

    def monitor_position(self, current_price):

        position = self.get_position()

        if position is None:

            return {
                "status": "NO_POSITION"
            }

        entry_price = float(
            position["entry_price"]
        )

        current_price = float(
            current_price
        )

        stop_price = (
            entry_price
            * (1.0 - self.stop_loss_pct)
        )

        target_price = (
            entry_price
            * (1.0 + self.take_profit_pct)
        )

        pnl = (
            current_price - entry_price
        ) * position["quantity"]

        if current_price <= stop_price:

            order = self.agent.execution_worker.broker.place_order(
                symbol=self.symbol,
                side="SELL",
                quantity=position["quantity"],
                price=current_price,
            )

            self.log_event(
                "STOP_LOSS",
                price=current_price,
                entry_price=entry_price,
                pnl=pnl,
                order=order,
            )

            return {
                "status": "STOP_LOSS",
                "order": order,
                "pnl": pnl,
            }

        if current_price >= target_price:

            order = self.agent.execution_worker.broker.place_order(
                symbol=self.symbol,
                side="SELL",
                quantity=position["quantity"],
                price=current_price,
            )

            self.log_event(
                "TAKE_PROFIT",
                price=current_price,
                entry_price=entry_price,
                pnl=pnl,
                order=order,
            )

            return {
                "status": "TAKE_PROFIT",
                "order": order,
                "pnl": pnl,
            }

        return {
            "status": "HOLD",
            "entry_price": entry_price,
            "current_price": current_price,
            "stop_price": stop_price,
            "target_price": target_price,
            "unrealized_pnl": pnl,
        }

    # ---------------------------------------------------------
    # STOP NEW ENTRIES
    # ---------------------------------------------------------

    def stop_new_entries(self):

        self.entries_enabled = False

        self.log_event(
            "NEW_ENTRIES_STOPPED"
        )

        return {
            "status": "COMPLETED"
        }

    # ---------------------------------------------------------
    # EOD
    # ---------------------------------------------------------

    def eod_exit(self, current_price):

        self.entries_enabled = False

        position = self.get_position()

        if position is None:

            self.log_event(
                "EOD_NO_POSITION"
            )

            return {
                "status": "NO_POSITION",
                "realized_pnl": self.agent.get_realized_pnl(),
            }

        result = self.agent.close_all_positions(
            current_prices={
                self.symbol: float(current_price)
            }
        )

        self.log_event(
            "EOD_EXIT",
            result=result,
        )

        return result

    # ---------------------------------------------------------
    # FULL SESSION
    # ---------------------------------------------------------

    def run_session(
        self,
        trading_date=None,
        entry_price=None,
        monitor_prices=None,
        eod_price=None,
    ):

        if monitor_prices is None:
            monitor_prices = []

        start_result = self.start(
            trading_date=trading_date
        )

        if start_result["status"] != "STARTED":

            return start_result

        results = {
            "start": start_result,
            "entry": None,
            "monitor": [],
            "eod": None,
        }

        if entry_price is not None:

            results["entry"] = self.run_entry_cycle()

        for price in monitor_prices:

            results["monitor"].append(
                self.monitor_position(price)
            )

            if self.get_position() is None:
                break

        self.stop_new_entries()

        if eod_price is not None:

            results["eod"] = self.eod_exit(
                eod_price
            )

        self.stop()

        return results

    # ---------------------------------------------------------
    # STATE
    # ---------------------------------------------------------

    def get_state(self):

        position = self.get_position()

        return {
            "running": self.running,
            "entries_enabled": self.entries_enabled,
            "current_date": (
                str(self.current_date)
                if self.current_date
                else None
            ),
            "symbol": self.symbol,
            "quantity": self.quantity,
            "position": position,
            "realized_pnl": self.agent.get_realized_pnl(),
            "daily_loss": self.get_daily_loss(),
            "max_daily_loss": self.max_daily_loss,
            "trade_count": self.trade_count,
            "event_count": len(self.events),
        }
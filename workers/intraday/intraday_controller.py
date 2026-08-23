import csv
import json

from datetime import datetime, date, time

from workers.calendar.market_calendar import (
    NSEMarketCalendar
)

from workers.intraday.candle_replay import (
    CandleReplay
)


class IntradayController:

    def __init__(
        self,
        pipeline,
        market_calendar=None,
        symbol="NIFTY",
        entry_cutoff="15:00",
        market_close="15:30",
    ):

        self.pipeline = pipeline

        self.calendar = (
            market_calendar
            or NSEMarketCalendar()
        )

        self.symbol = symbol

        self.entry_cutoff = self._parse_time(
            entry_cutoff
        )

        self.market_close = self._parse_time(
            market_close
        )

        self.events = []
        self.trades = []

        self.running = False
        self.entries_stopped = False
        self.current_date = None

        self.processed_candles = 0

    # ---------------------------------------------------------
    # TIME
    # ---------------------------------------------------------

    @staticmethod
    def _parse_time(value):

        if isinstance(value, time):
            return value

        return datetime.strptime(
            value,
            "%H:%M"
        ).time()

    @staticmethod
    def _candle_time(candle):

        value = candle["timestamp"]

        if isinstance(value, datetime):
            return value

        return datetime.fromisoformat(
            str(value)
        )

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def log_event(
        self,
        event,
        **details
    ):

        record = {
            "timestamp":
                datetime.now().isoformat(),

            "event": event,
            **details,
        }

        self.events.append(record)

        print(
            f"[INTRADAY] {event}"
        )

        return record

    # ---------------------------------------------------------
    # SESSION
    # ---------------------------------------------------------

    def start(
        self,
        trading_date=None
    ):

        if trading_date is None:
            trading_date = date.today()

        if not self.calendar.is_trading_day(
            trading_date
        ):

            reason = (
                self.calendar
                .get_market_day_reason(
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

        result = self.pipeline.start(
            trading_date
        )

        if result.get("status") == "STARTED":

            self.running = True
            self.current_date = trading_date

            self.log_event(
                "SESSION_STARTED",
                date=str(trading_date),
            )

        return result

    # ---------------------------------------------------------
    # DATA
    # ---------------------------------------------------------

    def load_replay(
        self,
        candles
    ):

        replay = CandleReplay(
            candles
        )

        self.log_event(
            "REPLAY_LOADED",
            candles=len(replay),
        )

        return replay

    # ---------------------------------------------------------
    # CANDLE PROCESSING
    # ---------------------------------------------------------

    def process_candle(
        self,
        candle,
        history
    ):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        candle_dt = self._candle_time(
            candle
        )

        candle_time = candle_dt.time()

        self.processed_candles += 1

        history.append(candle)

        self.log_event(
            "CANDLE_RECEIVED",
            candle_time=candle_dt.isoformat(),
            price=float(candle["close"]),
        )

        # -----------------------------------------------------
        # MARKET CLOSE
        # -----------------------------------------------------

        if candle_time >= self.market_close:

            if not self.entries_stopped:

                self.pipeline.stop_new_entries()

                self.entries_stopped = True

                self.log_event(
                    "ENTRY_CUTOFF_REACHED",
                    candle_time=candle_dt.isoformat(),
                )

            eod = self.pipeline.eod_exit(
                float(candle["close"])
            )

            self.log_event(
                "EOD_EXIT",
                result=eod,
            )

            return {
                "status": "MARKET_CLOSE",
                "candle": candle,
                "eod": eod,
            }

        # -----------------------------------------------------
        # ENTRY CUTOFF
        # -----------------------------------------------------

        if (
            candle_time >= self.entry_cutoff
            and not self.entries_stopped
        ):

            self.pipeline.stop_new_entries()

            self.entries_stopped = True

            self.log_event(
                "ENTRY_CUTOFF_REACHED",
                candle_time=candle_dt.isoformat(),
            )

        # -----------------------------------------------------
        # STRATEGY
        # -----------------------------------------------------

        if len(history) >= 10:

            agent = (
                self.pipeline
                .runtime
                .agent
            )

            agent.load_market_data(
                self.symbol,
                list(history),
            )

            strategy = (
                self.pipeline
                .run_strategy(
                    list(history)
                )
            )

            self.log_event(
                "STRATEGY_EVALUATED",
                candle_time=candle_dt.isoformat(),
                action=(
                    strategy
                    .get("signal", {})
                    .get("action")
                ),
                trend=(
                    strategy
                    .get("trend", {})
                    .get("trend")
                ),
            )

        else:

            strategy = {
                "status":
                    "INSUFFICIENT_DATA"
            }

        # -----------------------------------------------------
        # ENTRY
        # -----------------------------------------------------

        entry = None

        if (
            not self.entries_stopped
            and self.pipeline.runtime
                .get_position() is None
        ):

            entry = self.pipeline.run_entry()

            self.log_event(
                "ENTRY_EVALUATED",
                result=entry,
            )

            if entry.get("status") == "EXECUTED":

                self.trades.append(
                    {
                        "timestamp":
                            candle_dt.isoformat(),

                        "symbol":
                            self.symbol,

                        "side":
                            "BUY",

                        "price":
                            float(candle["close"]),

                        "status":
                            "OPENED",
                    }
                )

        # -----------------------------------------------------
        # POSITION MONITOR
        # -----------------------------------------------------

        monitor = None

        if (
            self.pipeline.runtime
            .get_position() is not None
        ):

            monitor = (
                self.pipeline
                .monitor(
                    float(candle["close"])
                )
            )

            if monitor.get("status") in (
                "TAKE_PROFIT",
                "STOP_LOSS",
            ):

                order = monitor.get(
                    "order",
                    {}
                )

                self.trades.append(
                    {
                        "timestamp":
                            candle_dt.isoformat(),

                        "symbol":
                            self.symbol,

                        "side":
                            "SELL",

                        "price":
                            float(candle["close"]),

                        "status":
                            monitor["status"],

                        "pnl":
                            float(
                                monitor.get(
                                    "pnl",
                                    0.0
                                )
                            ),
                    }
                )

        return {
            "status": "PROCESSED",
            "candle": candle,
            "strategy": strategy,
            "entry": entry,
            "monitor": monitor,
        }

    # ---------------------------------------------------------
    # FULL REPLAY
    # ---------------------------------------------------------

    def run_replay(
        self,
        replay
    ):

        if not self.running:

            return {
                "status": "STOPPED"
            }

        history = []
        results = []

        while replay.has_next():

            candle = replay.next()

            result = self.process_candle(
                candle,
                history
            )

            results.append(
                result
            )

            if result.get("status") == "MARKET_CLOSE":

                break

        self.log_event(
            "REPLAY_COMPLETED",
            processed_candles=(
                self.processed_candles
            ),
        )

        return {
            "status": "COMPLETED",
            "processed_candles":
                self.processed_candles,

            "results": results,
            "trades": list(self.trades),
        }

    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------

    def stop(self):

        if self.running:

            result = self.pipeline.stop()

        else:

            result = {
                "status": "STOPPED"
            }

        self.running = False

        self.log_event(
            "SESSION_STOPPED"
        )

        return result

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    def build_report(self):

        runtime_state = (
            self.pipeline
            .runtime
            .get_state()
        )

        return {
            "status": "COMPLETED",
            "symbol": self.symbol,
            "trading_date": (
                str(self.current_date)
                if self.current_date
                else None
            ),
            "processed_candles":
                self.processed_candles,

            "trade_count":
                len(self.trades),

            "realized_pnl":
                runtime_state[
                    "realized_pnl"
                ],

            "daily_loss":
                runtime_state[
                    "daily_loss"
                ],

            "position":
                runtime_state[
                    "position"
                ],

            "events":
                len(self.events),

            "entries_stopped":
                self.entries_stopped,
        }

    def save_reports(
        self,
        report_directory
    ):

        import os

        os.makedirs(
            report_directory,
            exist_ok=True
        )

        report = self.build_report()

        json_path = os.path.join(
            report_directory,
            "phase9_session_report.json"
        )

        events_path = os.path.join(
            report_directory,
            "phase9_events.csv"
        )

        trades_path = os.path.join(
            report_directory,
            "phase9_trades.csv"
        )

        with open(
            json_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=2
            )

        event_fields = [
            "timestamp",
            "event",
            "candle_time",
            "price",
            "action",
            "trend",
        ]

        with open(
            events_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=event_fields,
                extrasaction="ignore"
            )

            writer.writeheader()

            writer.writerows(
                self.events
            )

        trade_fields = [
            "timestamp",
            "symbol",
            "side",
            "price",
            "status",
            "pnl",
        ]

        with open(
            trades_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=trade_fields,
                extrasaction="ignore"
            )

            writer.writeheader()

            writer.writerows(
                self.trades
            )

        return {
            "json": json_path,
            "events_csv": events_path,
            "trades_csv": trades_path,
        }

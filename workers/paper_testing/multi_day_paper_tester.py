from datetime import date, datetime, timedelta


class MultiDayPaperTester:

    def __init__(
        self,
        controller_factory,
        replay_factory,
    ):

        self.controller_factory = (
            controller_factory
        )

        self.replay_factory = (
            replay_factory
        )

        self.results = []

    def run_day(self, trading_date):

        controller = (
            self.controller_factory()
        )

        candles = (
            self.replay_factory(
                trading_date
            )
        )

        started = controller.start(
            trading_date
        )

        if started.get("status") != "STARTED":

            return {
                "date": trading_date.isoformat(),
                "status": "FAILED",
                "reason": started,
                "trades": [],
                "realized_pnl": 0.0,
            }

        replay = controller.load_replay(
            candles
        )

        result = controller.run_replay(
            replay
        )

        state = (
            controller.pipeline.runtime.get_state()
        )

        day_result = {
            "date": trading_date.isoformat(),
            "status": result.get(
                "status",
                "UNKNOWN",
            ),
            "processed_candles": result.get(
                "processed_candles",
                0,
            ),
            "trade_count": len(
                controller.trades
            ),
            "entries": len([
                trade
                for trade in controller.trades
                if trade.get("side") == "BUY"
            ]),
            "exits": len([
                trade
                for trade in controller.trades
                if trade.get("side") == "SELL"
            ]),
            "realized_pnl": float(
                state.get(
                    "realized_pnl",
                    0.0,
                )
            ),
            "position_open": (
                state.get("position")
                is not None
            ),
            "entries_stopped": (
                controller.entries_stopped
            ),
            "event_count": len(
                controller.events
            ),
            "trades": list(
                controller.trades
            ),
        }

        controller.stop()

        self.results.append(
            day_result
        )

        return day_result

    def run_days(self, trading_dates):

        for trading_date in trading_dates:

            self.run_day(
                trading_date
            )

        return self.results

    def summary(self):

        total_pnl = sum(
            result["realized_pnl"]
            for result in self.results
        )

        total_trades = sum(
            result["trade_count"]
            for result in self.results
        )

        total_entries = sum(
            result["entries"]
            for result in self.results
        )

        total_exits = sum(
            result["exits"]
            for result in self.results
        )

        total_candles = sum(
            result["processed_candles"]
            for result in self.results
        )

        return {
            "days": len(
                self.results
            ),
            "total_candles": total_candles,
            "total_trades": total_trades,
            "total_entries": total_entries,
            "total_exits": total_exits,
            "total_realized_pnl": total_pnl,
            "all_sessions_completed": all(
                result["status"]
                == "COMPLETED"
                for result in self.results
            ),
            "all_positions_closed": all(
                result["position_open"]
                is False
                for result in self.results
            ),
            "all_entry_cutoffs": all(
                result["entries_stopped"]
                is True
                for result in self.results
            ),
        }

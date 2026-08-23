from datetime import datetime


class TradingScheduler:

    def __init__(
        self,
        daily_agent=None,
        symbol="NIFTY"
    ):
        self.daily_agent = daily_agent
        self.symbol = symbol
        self.running = False

    def start(self):

        self.running = True

        print("[SCHEDULER] Trading scheduler started")

    def stop(self):

        self.running = False

        print("[SCHEDULER] Trading scheduler stopped")

    def pre_market(self):

        print("[SCHEDULER] Pre-market phase")

        return {
            "status": "COMPLETED",
            "phase": "PRE_MARKET",
            "timestamp": datetime.now().isoformat()
        }

    def trading_session(self):

        print("[SCHEDULER] Trading session started")

        return {
            "status": "COMPLETED",
            "phase": "TRADING_SESSION",
            "timestamp": datetime.now().isoformat()
        }

    def stop_new_entries(self):

        print("[SCHEDULER] New entries stopped")

        return {
            "status": "COMPLETED",
            "phase": "STOP_NEW_ENTRIES",
            "timestamp": datetime.now().isoformat()
        }

    def eod_exit(self):

        print("[SCHEDULER] EOD exit phase")

        if self.daily_agent is None:

            return {
                "status": "SKIPPED",
                "reason": "NO_DAILY_AGENT"
            }

        current_price = (
            self.daily_agent.get_latest_price(
                self.symbol
            )
        )

        if current_price is None:

            return {
                "status": "SKIPPED",
                "reason": "NO_CURRENT_PRICE"
            }

        return self.daily_agent.run_eod_exit(
            current_prices={
                self.symbol: current_price
            }
        )

    def post_market(self):

        print("[SCHEDULER] Post-market phase")

        return {
            "status": "COMPLETED",
            "phase": "POST_MARKET",
            "timestamp": datetime.now().isoformat()
        }

    def run_cycle(self):

        if not self.running:

            return {
                "status": "STOPPED",
                "reason": "SCHEDULER_NOT_RUNNING"
            }

        print()
        print("=" * 60)
        print("DAILY SCHEDULE CYCLE")
        print("=" * 60)

        results = {}

        results["pre_market"] = (
            self.pre_market()
        )

        results["trading_session"] = (
            self.trading_session()
        )

        results["stop_new_entries"] = (
            self.stop_new_entries()
        )

        results["eod_exit"] = (
            self.eod_exit()
        )

        results["post_market"] = (
            self.post_market()
        )

        print()
        print("=" * 60)
        print("DAILY SCHEDULE CYCLE COMPLETE")
        print("=" * 60)

        return results
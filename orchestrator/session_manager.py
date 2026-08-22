from datetime import datetime, time


class SessionManager:

    PRE_MARKET_START = time(9, 0)
    MARKET_START = time(9, 15)
    NEW_ENTRY_END = time(15, 0)
    MARKET_CLOSE = time(15, 15)
    POST_MARKET_TIME = time(15, 30)

    def __init__(self, orchestrator):

        self.orchestrator = orchestrator

    def market_phase(self, current_time):

        current = current_time.time()

        if current < self.PRE_MARKET_START:

            return "SLEEP"

        if current < self.MARKET_START:

            return "PRE_MARKET"

        if current < self.NEW_ENTRY_END:

            return "TRADING"

        if current < self.MARKET_CLOSE:

            return "CLOSING"

        if current < self.POST_MARKET_TIME:

            return "POST_CLOSE"

        return "POST_MARKET"

    def run_phase(self, current_time):

        phase = self.market_phase(
            current_time
        )

        print(
            "\n=== MARKET PHASE ==="
        )

        print(
            "Time:",
            current_time.strftime("%H:%M")
        )

        print(
            "Phase:",
            phase
        )

        return phase

    def end_of_day(self, prices):

        print("\n=== END OF DAY ===")

        open_positions = (
            self.orchestrator.position_manager
            .get_open_positions()
        )

        if not open_positions:

            print("No open positions.")

            self.orchestrator.stop_trading()

            return {
                "status": "NO_POSITIONS",
                "closed_positions": []
            }

        closed_positions = []

        for position in open_positions:

            symbol = position["symbol"]

            exit_price = prices.get(symbol)

            if exit_price is None:

                print(
                    "No closing price for:",
                    symbol
                )

                continue

            closed = (
                self.orchestrator
                .position_manager
                .close_position(
                    symbol,
                    exit_price
                )
            )

            if closed is not None:

                closed_positions.append(
                    closed
                )

                print(
                    "Closed:",
                    symbol,
                    "@",
                    exit_price
                )

        self.orchestrator.stop_trading()

        return {
            "status": "COMPLETED",
            "closed_positions": closed_positions,
            "realized_pnl": (
                self.orchestrator
                .position_manager
                .get_realized_pnl()
            ),
            "completed_at": datetime.now().isoformat()
        }
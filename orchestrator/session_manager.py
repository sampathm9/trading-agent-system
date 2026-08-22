from datetime import datetime


class SessionManager:

    def __init__(self, orchestrator):

        self.orchestrator = orchestrator

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
                self.orchestrator.position_manager
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
class PositionMonitor:

    def __init__(self):
        self.positions = {}

    def register_position(self, position):
        symbol = position["symbol"]

        self.positions[symbol] = position

        return position

    def update_price(self, symbol, current_price):
        position = self.positions.get(symbol)

        if position is None:
            return None

        position["current_price"] = float(current_price)

        entry_price = float(
            position["entry_price"]
        )

        quantity = int(
            position["quantity"]
        )

        side = position["side"]

        if side == "BUY":
            pnl = (
                current_price - entry_price
            ) * quantity

        elif side == "SELL":
            pnl = (
                entry_price - current_price
            ) * quantity

        else:
            pnl = 0.0

        position["unrealized_pnl"] = round(
            pnl,
            2
        )

        return position

    def get_position(self, symbol):
        return self.positions.get(symbol)

    def remove_position(self, symbol):
        return self.positions.pop(
            symbol,
            None
        )

    def all_positions(self):
        return list(
            self.positions.values()
        )
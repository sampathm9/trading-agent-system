class PositionManager:

    def __init__(self):
        self.positions = {}
        self.realized_pnl = 0.0

    def add_position(
        self,
        symbol,
        side,
        quantity,
        entry_price
    ):

        self.positions[symbol] = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "entry_price": float(entry_price),
            "current_price": float(entry_price),
            "unrealized_pnl": 0.0
        }

        return self.positions[symbol]

    def update_price(self, symbol, current_price):

        position = self.positions.get(symbol)

        if position is None:
            return None

        position["current_price"] = float(current_price)

        entry = position["entry_price"]
        quantity = position["quantity"]
        side = position["side"]

        if side == "BUY":
            pnl = (current_price - entry) * quantity
        else:
            pnl = (entry - current_price) * quantity

        position["unrealized_pnl"] = pnl

        return position

    def close_position(self, symbol, exit_price):

        position = self.positions.get(symbol)

        if position is None:
            return None

        entry = position["entry_price"]
        quantity = position["quantity"]
        side = position["side"]

        if side == "BUY":
            pnl = (exit_price - entry) * quantity
        else:
            pnl = (entry - exit_price) * quantity

        self.realized_pnl += pnl

        closed_position = {
            **position,
            "exit_price": float(exit_price),
            "realized_pnl": pnl
        }

        del self.positions[symbol]

        return closed_position

    def get_position(self, symbol):

        return self.positions.get(symbol)

    def get_open_positions(self):

        return list(self.positions.values())

    def get_realized_pnl(self):

        return self.realized_pnl

    def get_total_unrealized_pnl(self):

        return sum(
            position["unrealized_pnl"]
            for position in self.positions.values()
        )

    def get_total_pnl(self):

        return (
            self.realized_pnl
            + self.get_total_unrealized_pnl()
        )
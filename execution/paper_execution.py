from datetime import datetime


class PaperExecution:

    def __init__(self):
        self.positions = {}
        self.trade_history = []

    def execute(self, decision, symbol, quantity, price):

        action = decision.get("action")

        if action not in ("BUY", "SELL"):
            return {
                "status": "REJECTED",
                "reason": "Invalid execution action"
            }

        if quantity <= 0:
            return {
                "status": "REJECTED",
                "reason": "Invalid quantity"
            }

        if price <= 0:
            return {
                "status": "REJECTED",
                "reason": "Invalid price"
            }

        position = {
            "symbol": symbol,
            "side": action,
            "quantity": quantity,
            "entry_price": float(price),
            "entry_time": datetime.now().isoformat()
        }

        self.positions[symbol] = position

        self.trade_history.append({
            "type": "ENTRY",
            **position
        })

        return {
            "status": "EXECUTED",
            "position": position
        }

    def exit_position(self, symbol, price):

        position = self.positions.get(symbol)

        if position is None:
            return {
                "status": "NO_POSITION",
                "reason": "No open position"
            }

        entry_price = position["entry_price"]
        quantity = position["quantity"]
        side = position["side"]

        if side == "BUY":
            pnl = (price - entry_price) * quantity
        else:
            pnl = (entry_price - price) * quantity

        exit_record = {
            "type": "EXIT",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "entry_price": entry_price,
            "exit_price": float(price),
            "pnl": pnl,
            "exit_time": datetime.now().isoformat()
        }

        self.trade_history.append(exit_record)

        del self.positions[symbol]

        return {
            "status": "CLOSED",
            **exit_record
        }

    def get_position(self, symbol):
        return self.positions.get(symbol)

    def get_open_positions(self):
        return list(self.positions.values())

    def get_trade_history(self):
        return self.trade_history
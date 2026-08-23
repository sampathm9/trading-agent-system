class PaperBroker:

    def __init__(self):
        self.orders = []
        self.positions = {}
        self.realized_pnl = 0.0

    def place_order(self, symbol, side, quantity, price):

        price = float(price)
        quantity = int(quantity)

        order = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "status": "FILLED"
        }

        if side == "BUY":

            existing = self.positions.get(symbol)

            if existing is None:

                self.positions[symbol] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "entry_price": price
                }

            else:

                old_quantity = existing["quantity"]
                old_price = existing["entry_price"]

                new_quantity = old_quantity + quantity

                average_price = (
                    (old_quantity * old_price)
                    + (quantity * price)
                ) / new_quantity

                existing["quantity"] = new_quantity
                existing["entry_price"] = average_price

        elif side == "SELL":

            existing = self.positions.get(symbol)

            if existing is None:

                order["status"] = "REJECTED"
                order["reason"] = "NO_OPEN_POSITION"

                print("[PAPER BROKER] SELL REJECTED")
                print(order)

                return order

            if quantity > existing["quantity"]:

                order["status"] = "REJECTED"
                order["reason"] = "INSUFFICIENT_POSITION"

                print("[PAPER BROKER] SELL REJECTED")
                print(order)

                return order

            pnl = (
                price - existing["entry_price"]
            ) * quantity

            self.realized_pnl += pnl

            existing["quantity"] -= quantity

            order["realized_pnl"] = pnl

            if existing["quantity"] == 0:
                del self.positions[symbol]

        else:

            order["status"] = "REJECTED"
            order["reason"] = "INVALID_SIDE"

            print("[PAPER BROKER] ORDER REJECTED")
            print(order)

            return order

        self.orders.append(order)

        print("[PAPER BROKER] ORDER FILLED")
        print(order)

        return order

    def get_orders(self):
        return self.orders

    def get_positions(self):
        return self.positions

    def get_position(self, symbol):
        return self.positions.get(symbol)

    def get_realized_pnl(self):
        return self.realized_pnl

    def calculate_unrealized_pnl(self, symbol, current_price):

        position = self.positions.get(symbol)

        if position is None:
            return 0.0

        return (
            float(current_price) - position["entry_price"]
        ) * position["quantity"]

    def close_all_positions(self, current_prices):

        print("[PAPER BROKER] Closing all paper positions")

        closing_orders = []

        for symbol, position in list(self.positions.items()):

            current_price = current_prices.get(symbol)

            if current_price is None:
                print(
                    f"[PAPER BROKER] No price available for {symbol}"
                )
                continue

            order = self.place_order(
                symbol=symbol,
                side="SELL",
                quantity=position["quantity"],
                price=current_price
            )

            closing_orders.append(order)

        return closing_orders
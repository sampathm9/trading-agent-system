class PaperBroker:

    def __init__(self):
        self.orders = []
        self.positions = []

    def place_order(self, symbol, side, quantity, price):

        order = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'status': 'FILLED'
        }

        self.orders.append(order)

        print('[PAPER BROKER] ORDER FILLED')
        print(order)

        return order

    def get_orders(self):
        return self.orders

    def get_positions(self):
        return self.positions

    def close_all_positions(self):
        print('[PAPER BROKER] Closing all paper positions')
        self.positions.clear()

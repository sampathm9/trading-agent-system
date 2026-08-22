class PositionManager:

    def __init__(self):
        self.position = None

    def open(self, symbol, side, quantity, price):
        if self.position is not None:
            return False

        self.position = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'entry_price': price
        }

        return True

    def close(self, price):
        if self.position is None:
            return None

        position = self.position

        if position['side'] == 'BUY':
            pnl = (price - position['entry_price']) * position['quantity']
        else:
            pnl = (position['entry_price'] - price) * position['quantity']

        self.position = None

        return {
            'symbol': position['symbol'],
            'side': position['side'],
            'quantity': position['quantity'],
            'entry_price': position['entry_price'],
            'exit_price': price,
            'pnl': pnl
        }

    def get_position(self):
        return self.position

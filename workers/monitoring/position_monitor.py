class PositionMonitor:

    def __init__(self, stop_loss=100.0, take_profit=200.0):
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def check(self, position, current_price, strategy_exit=False, market_regime='UNKNOWN', force_exit=False):

        if position is None:
            return {
                'action': 'NONE',
                'reason': 'No open position'
            }

        entry_price = position['entry_price']
        side = position['side']

        if side == 'BUY':
            pnl = current_price - entry_price
        else:
            pnl = entry_price - current_price

        if force_exit:
            return {
                'action': 'EXIT',
                'reason': 'Mandatory end-of-day exit',
                'pnl': pnl
            }

        if pnl <= -self.stop_loss:
            return {
                'action': 'EXIT',
                'reason': 'Stop-loss triggered',
                'pnl': pnl
            }

        if pnl >= self.take_profit:
            return {
                'action': 'EXIT',
                'reason': 'Take-profit triggered',
                'pnl': pnl
            }

        if strategy_exit:
            return {
                'action': 'EXIT',
                'reason': 'Strategy exit signal',
                'pnl': pnl
            }

        if market_regime == 'VOLATILE_RANGE':
            return {
                'action': 'EXIT',
                'reason': 'Risky market regime',
                'pnl': pnl
            }

        return {
            'action': 'HOLD',
            'reason': 'Position conditions acceptable',
            'pnl': pnl
        }

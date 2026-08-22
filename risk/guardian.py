class RiskGuardian:

    def __init__(self, max_daily_loss=1000, max_position_size=1):
        self.max_daily_loss = max_daily_loss
        self.max_position_size = max_position_size

    def approve(self, quantity, current_daily_loss):

        if current_daily_loss >= self.max_daily_loss:
            print('[RISK] Daily loss limit reached')
            return False

        if quantity > self.max_position_size:
            print('[RISK] Position size rejected')
            return False

        if quantity <= 0:
            print('[RISK] Invalid quantity')
            return False

        print('[RISK] Trade approved')
        return True

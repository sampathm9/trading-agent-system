class RiskWorker:

    def validate(self, action, quantity, max_quantity=100):

        if action not in ["BUY", "SELL"]:
            return False

        if quantity <= 0:
            return False

        if quantity > max_quantity:
            return False

        return True
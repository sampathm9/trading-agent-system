class RiskEngine:

    def __init__(
        self,
        max_quantity=10,
        min_confidence=0.60,
        max_daily_loss=1000
    ):
        self.max_quantity = max_quantity
        self.min_confidence = min_confidence
        self.max_daily_loss = max_daily_loss

    def validate(
        self,
        decision,
        quantity,
        daily_pnl=0
    ):
        action = decision.get("action", "HOLD")
        confidence = float(
            decision.get("confidence", 0)
        )

        if action == "HOLD":
            return {
                "approved": False,
                "reason": "No trade signal"
            }

        if quantity <= 0:
            return {
                "approved": False,
                "reason": "Invalid quantity"
            }

        if quantity > self.max_quantity:
            return {
                "approved": False,
                "reason": "Quantity exceeds risk limit"
            }

        if confidence < self.min_confidence:
            return {
                "approved": False,
                "reason": "Confidence below minimum"
            }

        if daily_pnl <= -self.max_daily_loss:
            return {
                "approved": False,
                "reason": "Daily loss limit reached"
            }

        if action not in ["BUY", "SELL"]:
            return {
                "approved": False,
                "reason": "Invalid trading action"
            }

        return {
            "approved": True,
            "reason": "Risk checks passed"
        }
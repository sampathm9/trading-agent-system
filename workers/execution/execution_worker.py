from datetime import datetime
from execution.paper_broker import PaperBroker
from risk.guardian import RiskGuardian

class ExecutionWorker:

    def __init__(self, broker=None, risk_guardian=None):
        self.broker = broker or PaperBroker()
        self.risk_guardian = risk_guardian or RiskGuardian()

    def execute(self, decision, symbol, quantity, price, daily_loss=0.0):

        action = decision.get('action')

        if action not in ('BUY', 'SELL'):
            return {
                'status': 'SKIPPED',
                'reason': 'No executable action'
            }

        approved = self.risk_guardian.approve(
            quantity,
            daily_loss
        )

        if not approved:
            return {
                'status': 'REJECTED',
                'reason': 'Risk Guardian rejected order'
            }

        order = self.broker.place_order(
            symbol=symbol,
            side=action,
            quantity=quantity,
            price=price
        )

        return {
            'status': 'EXECUTED',
            'timestamp': datetime.now().isoformat(),
            'order': order
        }

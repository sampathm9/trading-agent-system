from datetime import datetime
from database.database import initialize_database
from events.event_bus import EventBus
from events.events import create_event
from risk.guardian import RiskGuardian
from execution.paper_broker import PaperBroker

class TradingOrchestrator:

    def __init__(self):
        self.mode = 'PAPER'
        self.event_bus = EventBus()
        self.risk_guardian = RiskGuardian(max_daily_loss=1000, max_position_size=1)
        self.broker = PaperBroker()
        initialize_database()
        self._register_events()

    def _register_events(self):
        self.event_bus.subscribe('system.started', self._on_system_started)

    def _on_system_started(self, event):
        print('[EVENT] System started event received')

    def start(self):
        print('=' * 60)
        print('TRADING AGENT SYSTEM')
        print('=' * 60)
        print(f'Mode: {self.mode}')
        print(f'Started: {datetime.now()}')
        print()
        print('Initializing system...')
        print('[OK] Database')
        print('[OK] Event Bus')
        print('[OK] Risk Guardian')
        print('[OK] Paper Broker')
        print()
        print('System status: READY')
        event = create_event('system.started', {'mode': self.mode})
        self.event_bus.publish(event)

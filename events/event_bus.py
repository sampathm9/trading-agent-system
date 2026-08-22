from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class Event:
    name: str
    data: dict[str, Any]
    created_at: datetime

class EventBus:

    def __init__(self):
        self.handlers = {}

    def subscribe(self, event_name, handler):
        self.handlers.setdefault(event_name, []).append(handler)

    def publish(self, event: Event):
        handlers = self.handlers.get(event.name, [])

        for handler in handlers:
            handler(event)

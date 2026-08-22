from datetime import datetime
from events.event_bus import Event

def create_event(name, data=None):
    return Event(
        name=name,
        data=data or {},
        created_at=datetime.now()
    )

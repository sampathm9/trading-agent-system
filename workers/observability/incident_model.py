from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass
class Incident:
    incident_id: str
    severity: str
    component: str
    incident_type: str
    message: str
    timestamp: str
    recovered: bool = False
    recovery_action: str = ""
    recovery_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

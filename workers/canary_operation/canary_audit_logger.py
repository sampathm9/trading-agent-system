from datetime import datetime
from typing import Dict, List


class CanaryAuditLogger:

    def __init__(self):
        self.events: List[Dict] = []

    def log(
        self,
        event: str,
        details: Dict = None,
    ) -> Dict:

        record = {
            "timestamp": datetime.utcnow().isoformat()
            + "Z",
            "event": str(event),
            "details": details or {},
        }

        self.events.append(record)

        return record

    def export(
        self,
        path: str,
    ):

        from pathlib import Path
        import json

        target = Path(path)
        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with target.open(
            "w",
            encoding="utf-8",
        ) as handle:

            for event in self.events:
                handle.write(
                    json.dumps(
                        event,
                        default=str,
                    )
                    + "\n"
                )

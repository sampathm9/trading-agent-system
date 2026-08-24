import json
from datetime import datetime
from pathlib import Path


class RuntimeAuditLogger:

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(self, event, details=None):

        record = {
            "timestamp": datetime.utcnow().isoformat()
            + "Z",
            "event": event,
            "details": details or {},
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                json.dumps(
                    record,
                    sort_keys=True,
                )
                + "\n"
            )

        return record

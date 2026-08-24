import json
from datetime import datetime
from pathlib import Path
from typing import Dict


class ReleaseAuditLogger:

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(
        self,
        event: str,
        details: Dict,
    ):

        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "details": details,
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                json.dumps(record)
                + "\n"
            )

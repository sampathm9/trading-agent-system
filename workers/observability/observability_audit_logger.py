from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
import json


class ObservabilityAuditLogger:

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(
        self,
        event: str,
        payload: Dict[str, Any] | None = None,
    ) -> None:

        record = {
            "timestamp":
                datetime.now(timezone.utc).isoformat(),
            "event": event,
            "payload": payload or {},
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

# ============================================================
# PHASE 26 - AUDIT LOGGER
# ============================================================

from datetime import datetime
from pathlib import Path
from typing import Dict
import json


class CanaryRollbackAuditLogger:

    def __init__(
        self,
        path: str,
    ):

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(
        self,
        event: str,
        payload: Dict,
    ) -> None:

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "payload": payload,
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                json.dumps(
                    record,
                    default=str,
                )
                + "\n"
            )

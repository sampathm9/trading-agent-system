from pathlib import Path
from datetime import datetime
from typing import Dict


class ActivationAuditLogger:

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
        details: Dict | None = None,
    ) -> Dict:

        record = {
            "timestamp": datetime.now().isoformat(),
            "event": str(event),
            "details": details or {},
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(
                str(record)
                + "\n"
            )

        return record

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict


class Phase20AuditLogger:

    def __init__(
        self,
        directory: str,
        filename: str,
    ):

        self.directory = Path(
            directory
        )

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path = (
            self.directory
            / filename
        )

    def log(
        self,
        event_type: str,
        data: Dict,
    ) -> Dict:

        event = {
            "timestamp": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "event_type": event_type,
            "data": data,
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                json.dumps(
                    event,
                    default=str,
                )
                + "\n"
            )

        return event

    def read_events(self):

        if not self.path.exists():

            return []

        events = []

        for line in self.path.read_text(
            encoding="utf-8"
        ).splitlines():

            if line.strip():

                events.append(
                    json.loads(line)
                )

        return events

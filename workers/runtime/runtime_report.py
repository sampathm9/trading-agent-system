import json
from pathlib import Path
from datetime import datetime


class RuntimeReportWriter:

    def __init__(self, directory, filename):

        self.path = (
            Path(directory) / filename
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write(self, report):

        payload = {
            "generated_at":
                datetime.utcnow().isoformat()
                + "Z",
            **report,
        }

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                payload,
                handle,
                indent=2,
                sort_keys=True,
            )

        return self.path

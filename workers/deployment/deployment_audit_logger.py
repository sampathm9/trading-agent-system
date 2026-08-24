from datetime import datetime
from pathlib import Path
from typing import Dict

from config.phase22_config import (
    REPORT_DIRECTORY,
    AUDIT_FILENAME,
)


class DeploymentAuditLogger:

    def __init__(self):

        directory = Path(REPORT_DIRECTORY)
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path = directory / AUDIT_FILENAME

    def log(
        self,
        event: str,
        details: Dict | None = None,
    ):

        timestamp = datetime.now().isoformat()

        line = (
            f"{timestamp} | "
            f"{event} | "
            f"{details or {}}\n"
        )

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as handle:

            handle.write(line)

    def get_path(self) -> str:

        return str(self.path)

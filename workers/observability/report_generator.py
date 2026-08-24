import json
from pathlib import Path
from typing import Dict, Any


class ObservabilityReport:

    def __init__(
        self,
        directory: str,
        filename: str,
    ):

        self.directory = Path(directory)
        self.filename = filename

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write(
        self,
        payload: Dict[str, Any],
    ) -> str:

        path = self.directory / self.filename

        with path.open(
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                payload,
                handle,
                indent=2,
                sort_keys=True,
            )

        return str(path)

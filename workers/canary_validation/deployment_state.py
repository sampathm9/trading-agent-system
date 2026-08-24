# ============================================================
# PHASE 26 - DEPLOYMENT STATE
# ============================================================

import json
from pathlib import Path
from typing import Dict


class CanaryDeploymentState:

    def __init__(
        self,
        path: str,
    ):

        self.path = Path(path)

    def save(
        self,
        state: Dict,
    ) -> str:

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            json.dumps(
                state,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(
            self.path
        )

    def load(self) -> Dict:

        if not self.path.exists():

            return {
                "state": "UNKNOWN"
            }

        return json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

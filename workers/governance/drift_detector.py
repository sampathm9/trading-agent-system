import hashlib
import json
from typing import Any, Dict


class DriftDetector:

    def fingerprint(
        self,
        values: Dict[str, Any],
    ) -> str:

        canonical = json.dumps(
            values,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

    def compare(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any],
    ) -> Dict[str, Any]:

        baseline_hash = self.fingerprint(baseline)
        current_hash = self.fingerprint(current)

        return {
            "drift_detected": (
                baseline_hash != current_hash
            ),
            "baseline_hash": baseline_hash,
            "current_hash": current_hash,
            "passed": baseline_hash == current_hash,
        }

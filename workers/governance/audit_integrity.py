import hashlib
import json
from typing import Any, Dict, List


class AuditIntegrity:

    def __init__(self):

        self.events: List[Dict[str, Any]] = []

    def record(
        self,
        event_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:

        event = {
            "sequence": len(self.events) + 1,
            "event_type": str(event_type),
            "details": details,
        }

        canonical = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
        )

        event["hash"] = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        self.events.append(event)

        return event

    def verify(self) -> Dict[str, Any]:

        errors = []

        for index, event in enumerate(
            self.events,
            start=1,
        ):

            stored_hash = event.get("hash")

            copy = dict(event)
            copy.pop("hash", None)

            canonical = json.dumps(
                copy,
                sort_keys=True,
                separators=(",", ":"),
            )

            expected_hash = hashlib.sha256(
                canonical.encode("utf-8")
            ).hexdigest()

            if event.get("sequence") != index:
                errors.append(
                    f"Invalid sequence at event {index}"
                )

            if stored_hash != expected_hash:
                errors.append(
                    f"Invalid hash at event {index}"
                )

        return {
            "passed": len(errors) == 0,
            "event_count": len(self.events),
            "errors": errors,
        }

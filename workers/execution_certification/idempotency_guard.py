from typing import Dict


class Phase21IdempotencyGuard:

    def __init__(self):

        self.processed_keys = set()

    def check(
        self,
        idempotency_key: str,
    ) -> Dict:

        key = str(
            idempotency_key
        ).strip()

        if not key:

            return {
                "allowed": False,
                "duplicate": False,
                "reason": (
                    "Idempotency key is required."
                ),
            }

        if key in self.processed_keys:

            return {
                "allowed": False,
                "duplicate": True,
                "reason": (
                    "Duplicate order blocked."
                ),
            }

        return {
            "allowed": True,
            "duplicate": False,
            "reason": (
                "New idempotency key."
            ),
        }

    def register(
        self,
        idempotency_key: str,
    ):

        key = str(
            idempotency_key
        ).strip()

        if key:
            self.processed_keys.add(
                key
            )

    def count(self) -> int:

        return len(
            self.processed_keys
        )

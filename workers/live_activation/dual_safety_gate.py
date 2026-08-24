from typing import Dict


class DualSafetyGate:

    def __init__(self):

        self.primary_enabled = True
        self.secondary_enabled = True

    def evaluate(
        self,
        primary: bool,
        secondary: bool,
    ) -> Dict:

        self.primary_enabled = bool(primary)
        self.secondary_enabled = bool(
            secondary
        )

        allowed = (
            self.primary_enabled
            and self.secondary_enabled
        )

        return {
            "allowed": allowed,
            "primary_gate": self.primary_enabled,
            "secondary_gate": self.secondary_enabled,
        }

    def emergency_shutdown(self):

        self.primary_enabled = False
        self.secondary_enabled = False

        return {
            "allowed": False,
            "reason": "Emergency shutdown active",
        }

    def recover(self):

        self.primary_enabled = True
        self.secondary_enabled = True

        return {
            "allowed": True,
            "reason": "Safety gates recovered",
        }

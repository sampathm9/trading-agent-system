from typing import Dict


class EmergencyShutdownController:

    def __init__(self):

        self.active = False
        self.reason = ""

    def trigger(
        self,
        reason: str,
    ) -> Dict:

        self.active = True
        self.reason = str(reason)

        return {
            "active": True,
            "reason": self.reason,
        }

    def recover(self) -> Dict:

        self.active = False
        self.reason = ""

        return {
            "active": False,
            "reason": "Emergency shutdown cleared",
        }

    def can_execute(self) -> bool:

        return not self.active

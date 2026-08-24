from typing import Dict


class RollbackController:

    def __init__(self):

        self.rollback_active = False
        self.reason = ""

    def trigger(
        self,
        reason: str,
    ) -> Dict:

        self.rollback_active = True
        self.reason = str(reason)

        return {
            "rollback": True,
            "reason": self.reason,
        }

    def reset(self) -> Dict:

        self.rollback_active = False
        self.reason = ""

        return {
            "rollback": False,
            "reason": "Rollback cleared",
        }

    def can_continue(self) -> bool:

        return not self.rollback_active

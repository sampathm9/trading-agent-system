from typing import Dict


class Phase21KillSwitch:

    def __init__(
        self,
        enabled: bool = True,
        active: bool = False,
    ):

        self.enabled = bool(
            enabled
        )

        self.active = bool(
            active
        )

        self.reason = ""

    def activate(
        self,
        reason: str = "Manual kill switch",
    ):

        if not self.enabled:
            return False

        self.active = True
        self.reason = str(reason)

        return True

    def deactivate(self):

        self.active = False
        self.reason = ""

    def status(self) -> Dict:

        return {
            "enabled": self.enabled,
            "active": self.active,
            "reason": self.reason,
        }

    def can_execute(self) -> Dict:

        if not self.enabled:

            return {
                "allowed": False,
                "reason": (
                    "Kill switch must be enabled."
                ),
            }

        if self.active:

            return {
                "allowed": False,
                "reason": (
                    self.reason
                    or "Kill switch active."
                ),
            }

        return {
            "allowed": True,
            "reason": (
                "Kill switch inactive."
            ),
        }

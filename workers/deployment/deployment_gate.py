from typing import Dict


class DeploymentGate:

    def __init__(self):

        self.enabled = False
        self.reason = "Deployment gate has not been opened"

    def open(
        self,
        validation: Dict,
    ) -> Dict:

        if not validation.get("valid", False):

            self.enabled = False
            self.reason = "Deployment configuration invalid"

            return {
                "allowed": False,
                "reason": self.reason,
            }

        self.enabled = True
        self.reason = "Deployment gate opened"

        return {
            "allowed": True,
            "reason": self.reason,
        }

    def close(
        self,
        reason: str = "Deployment gate closed",
    ):

        self.enabled = False
        self.reason = reason

    def can_deploy(self) -> Dict:

        return {
            "allowed": self.enabled,
            "reason": self.reason,
        }

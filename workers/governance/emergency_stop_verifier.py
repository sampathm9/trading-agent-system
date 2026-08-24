from typing import Any, Dict


class EmergencyStopVerifier:

    def __init__(self):

        self.emergency_stop = False

    def activate(self) -> None:

        self.emergency_stop = True

    def recover(self) -> None:

        self.emergency_stop = False

    def can_execute(self) -> bool:

        return not self.emergency_stop

    def verify(self) -> Dict[str, Any]:

        self.activate()

        blocked = not self.can_execute()

        self.recover()

        recovered = self.can_execute()

        return {
            "passed": blocked and recovered,
            "blocked_during_stop": blocked,
            "recovered_after_reset": recovered,
        }

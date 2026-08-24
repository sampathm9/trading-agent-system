from typing import Dict, Any, Callable


class RecoveryEngine:

    def __init__(
        self,
        max_attempts: int = 3,
        enabled: bool = True,
    ):

        self.max_attempts = int(max_attempts)
        self.enabled = bool(enabled)

        self.recovery_attempts = 0
        self.recoveries = 0
        self.failed_recoveries = 0

    def recover(
        self,
        component: str,
        recovery_callback: Callable[[], bool] | None = None,
    ) -> Dict[str, Any]:

        if not self.enabled:
            return {
                "component": component,
                "recovered": False,
                "reason": "AUTO_RECOVERY_DISABLED",
                "attempts": 0,
            }

        attempts = 0

        while attempts < self.max_attempts:

            attempts += 1
            self.recovery_attempts += 1

            try:
                success = (
                    recovery_callback()
                    if recovery_callback
                    else True
                )
            except Exception:
                success = False

            if success:

                self.recoveries += 1

                return {
                    "component": component,
                    "recovered": True,
                    "reason": "RECOVERY_SUCCESSFUL",
                    "attempts": attempts,
                }

        self.failed_recoveries += 1

        return {
            "component": component,
            "recovered": False,
            "reason": "RECOVERY_FAILED",
            "attempts": attempts,
        }

    def snapshot(self) -> Dict[str, int]:
        return {
            "recovery_attempts": self.recovery_attempts,
            "successful_recoveries": self.recoveries,
            "failed_recoveries": self.failed_recoveries,
        }

from typing import Dict


class FinalReleaseGate:

    def __init__(
        self,
        config,
        safety_controller,
        phase_verifier,
    ):
        self.config = config
        self.safety = safety_controller
        self.phase_verifier = phase_verifier

    def evaluate(self) -> Dict:

        safety = self.safety.validate()

        phases = self.phase_verifier.verify_required_phases()

        checks = {
            "safety": safety["passed"],
            "required_phase_reports": phases["passed"],
            "human_approval_required": (
                self.config.REQUIRE_HUMAN_RELEASE_APPROVAL
                is True
            ),
            "automatic_live_activation_disabled": (
                self.config.ALLOW_AUTOMATIC_LIVE_ACTIVATION
                is False
            ),
        }

        passed = all(checks.values())

        return {
            "ready": passed,
            "classification": (
                "FINAL_RELEASE_CERTIFIED"
                if passed
                else "RELEASE_BLOCKED"
            ),
            "score": (
                sum(
                    1 for value in checks.values()
                    if value
                ) / len(checks)
            ),
            "checks": checks,
            "safety": safety,
            "phase_reports": phases,
        }

from typing import Dict


class ActivationConfigValidator:

    def validate(self, config_module) -> Dict:

        errors = []

        required = {
            "PHASE24_ENABLED": True,
            "REQUIRE_EXPLICIT_ACTIVATION": True,
            "REQUIRE_MANUAL_APPROVAL": True,
            "REQUIRE_BROKER_AUTHORIZATION": True,
            "REQUIRE_POSITION_RECONCILIATION": True,
            "REQUIRE_HEALTHY_RUNTIME": True,
        }

        for key, expected in required.items():

            actual = getattr(
                config_module,
                key,
                None,
            )

            if actual != expected:

                errors.append(
                    f"{key} must be {expected}"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

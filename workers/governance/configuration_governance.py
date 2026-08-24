from typing import Any, Dict


class ConfigurationGovernance:

    REQUIRED_VALUES = {
        "LIVE_TRADING_ENABLED": False,
        "REAL_BROKER_ENABLED": False,
        "PLACE_REAL_ORDERS": False,
        "PAPER_ONLY": True,
    }

    def validate(self, config_module) -> Dict[str, Any]:

        errors = []
        checks = {}

        for name, expected in self.REQUIRED_VALUES.items():

            actual = getattr(config_module, name, None)

            passed = actual == expected

            checks[name] = {
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }

            if not passed:
                errors.append(
                    f"{name}: expected {expected}, got {actual}"
                )

        phase_enabled = getattr(
            config_module,
            "PHASE29_ENABLED",
            False,
        )

        checks["PHASE29_ENABLED"] = {
            "expected": True,
            "actual": phase_enabled,
            "passed": phase_enabled is True,
        }

        if phase_enabled is not True:
            errors.append("PHASE29_ENABLED must be True")

        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }

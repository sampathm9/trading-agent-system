class RuntimeSafety:

    def __init__(self, config):
        self.config = config
        self.emergency_stop = False

    def validate(self):

        failures = []

        if not self.config.SHADOW_MODE:
            failures.append(
                "SHADOW_MODE must remain enabled"
            )

        if self.config.LIVE_TRADING_ENABLED:
            failures.append(
                "LIVE_TRADING_ENABLED must be False"
            )

        if self.config.REAL_BROKER_ENABLED:
            failures.append(
                "REAL_BROKER_ENABLED must be False"
            )

        if self.config.PLACE_REAL_ORDERS:
            failures.append(
                "PLACE_REAL_ORDERS must be False"
            )

        if self.config.RUNTIME_ACTIVATION_ENABLED:
            failures.append(
                "RUNTIME_ACTIVATION_ENABLED must be False"
            )

        return {
            "safe": len(failures) == 0,
            "failures": failures,
        }

    def activate_emergency_stop(self):
        self.emergency_stop = True
        return True

    def clear_emergency_stop(self):
        self.emergency_stop = False
        return True

    def can_run(self):

        if self.emergency_stop:
            return False

        result = self.validate()

        return bool(result["safe"])

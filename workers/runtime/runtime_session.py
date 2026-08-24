class RuntimeSessionController:

    def __init__(
        self,
        state_machine,
        safety,
        audit_logger,
    ):
        self.state_machine = state_machine
        self.safety = safety
        self.audit = audit_logger

        self.candles_processed = 0
        self.trades_processed = 0
        self.errors = []

    def start(self):

        if not self.safety.can_run():

            self.state_machine.transition(
                "FAILED"
            )

            self.audit.log(
                "RUNTIME_START_BLOCKED"
            )

            return {
                "started": False,
                "reason": "runtime safety rejected startup",
            }

        self.state_machine.transition(
            "RUNNING"
        )

        self.audit.log(
            "RUNTIME_STARTED"
        )

        return {
            "started": True,
            "state": self.state_machine.state.value,
        }

    def process_candle(self):

        if not self.state_machine.is_running():
            return False

        self.candles_processed += 1

        return True

    def record_trade(self):

        if not self.state_machine.is_running():
            return False

        self.trades_processed += 1

        return True

    def stop(self):

        if self.state_machine.is_stopped():
            return False

        self.state_machine.transition(
            "STOPPING"
        )

        self.audit.log(
            "RUNTIME_STOPPING"
        )

        self.state_machine.transition(
            "STOPPED"
        )

        self.audit.log(
            "RUNTIME_STOPPED"
        )

        return True

    def emergency_shutdown(self):

        self.safety.activate_emergency_stop()

        self.state_machine.transition(
            "EMERGENCY_STOP"
        )

        self.audit.log(
            "EMERGENCY_SHUTDOWN",
            {
                "reason":
                    "Emergency shutdown activated"
            },
        )

        return True

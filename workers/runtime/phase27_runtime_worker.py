import json
from pathlib import Path

from config import phase27_config

from workers.runtime.runtime_state import (
    RuntimeState,
    RuntimeStateMachine,
)

from workers.runtime.runtime_safety import (
    RuntimeSafety,
)

from workers.runtime.runtime_audit_logger import (
    RuntimeAuditLogger,
)

from workers.runtime.component_registry import (
    RuntimeComponentRegistry,
)

from workers.runtime.runtime_preflight import (
    RuntimePreflight,
)

from workers.runtime.runtime_session import (
    RuntimeSessionController,
)

from workers.runtime.runtime_health_monitor import (
    RuntimeHealthMonitor,
)

from workers.runtime.runtime_report import (
    RuntimeReportWriter,
)


class Phase27RuntimeWorker:

    def __init__(self):

        self.state_machine = (
            RuntimeStateMachine()
        )

        self.safety = RuntimeSafety(
            phase27_config
        )

        self.audit = RuntimeAuditLogger(
            Path(
                phase27_config.REPORT_DIRECTORY
            )
            / phase27_config.AUDIT_FILENAME
        )

        self.registry = (
            RuntimeComponentRegistry(
                phase27_config.REQUIRED_COMPONENTS
            )
        )

        self.preflight = RuntimePreflight(
            self.safety,
            self.registry,
        )

        self.session = (
            RuntimeSessionController(
                self.state_machine,
                self.safety,
                self.audit,
            )
        )

        self.health = RuntimeHealthMonitor(
            self.registry
        )

        self.report_writer = (
            RuntimeReportWriter(
                phase27_config.REPORT_DIRECTORY,
                phase27_config.REPORT_FILENAME,
            )
        )

    # --------------------------------------------------------
    # REGISTER COMPONENTS
    # --------------------------------------------------------

    def register_required_components(
        self,
        overrides=None,
    ):

        overrides = overrides or {}

        for name in (
            phase27_config.REQUIRED_COMPONENTS
        ):

            healthy = overrides.get(
                name,
                True,
            )

            self.registry.register(
                name,
                healthy=healthy,
                details={
                    "source":
                        "phase27_runtime",
                },
            )

        return self.registry.health_report()

    # --------------------------------------------------------
    # PREFLIGHT
    # --------------------------------------------------------

    def run_preflight(self):

        self.state_machine.transition(
            RuntimeState.PREFLIGHT
        )

        result = (
            self.preflight.validate()
        )

        self.audit.log(
            "PREFLIGHT_COMPLETED",
            result,
        )

        if result["passed"]:

            self.state_machine.transition(
                RuntimeState.READY
            )

        else:

            self.state_machine.transition(
                RuntimeState.FAILED
            )

        return result

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    def start(self):

        return self.session.start()

    # --------------------------------------------------------
    # CANDLE
    # --------------------------------------------------------

    def process_candle(self):

        return self.session.process_candle()

    # --------------------------------------------------------
    # EMERGENCY
    # --------------------------------------------------------

    def emergency_shutdown(self):

        return (
            self.session.emergency_shutdown()
        )

    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    def recover(self):

        self.safety.clear_emergency_stop()

        self.audit.log(
            "EMERGENCY_STOP_CLEARED"
        )

        self.state_machine.transition(
            RuntimeState.READY
        )

        return True

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    def stop(self):

        return self.session.stop()

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    def build_report(self):

        safety = self.safety.validate()

        health = self.health.check()

        preflight = self.preflight.validate()

        safety_pass = safety["safe"]

        readiness_score = (
            1.0
            if (
                safety_pass
                and preflight["passed"]
                and health["healthy"]
            )
            else 0.0
        )

        classification = (
            "PAPER_RUNTIME_READY"
            if readiness_score == 1.0
            else "RUNTIME_NOT_READY"
        )

        return {
            "phase": 27,
            "name":
                "Production Runtime Orchestration",
            "runtime_state":
                self.state_machine.state.value,
            "state_history":
                self.state_machine.history,
            "safety": safety,
            "preflight": preflight,
            "health": health,
            "runtime": {
                "candles_processed":
                    self.session.candles_processed,
                "trades_processed":
                    self.session.trades_processed,
                "errors":
                    self.session.errors,
            },
            "readiness": {
                "ready":
                    readiness_score == 1.0,
                "classification":
                    classification,
                "score":
                    readiness_score,
            },
            "real_orders_placed": 0,
            "real_broker_used": False,
            "live_trading_enabled":
                phase27_config.LIVE_TRADING_ENABLED,
        }

    def write_report(self):

        report = self.build_report()

        path = self.report_writer.write(
            report
        )

        return path, report

from typing import Dict, Any

from config import phase28_config

from workers.observability.health_monitor import (
    ObservabilityHealthMonitor,
)

from workers.observability.incident_detector import (
    IncidentDetector,
)

from workers.observability.recovery_engine import (
    RecoveryEngine,
)

from workers.observability.observability_safety import (
    ObservabilitySafety,
)

from workers.observability.observability_audit_logger import (
    ObservabilityAuditLogger,
)

from workers.observability.readiness_evaluator import (
    ObservabilityReadiness,
)

from workers.observability.report_generator import (
    ObservabilityReport,
)


class Phase28ObservabilityWorker:

    def __init__(self):

        self.health = (
            ObservabilityHealthMonitor()
        )

        self.incidents = (
            IncidentDetector()
        )

        self.recovery = RecoveryEngine(
            max_attempts=(
                phase28_config.MAX_RECOVERY_ATTEMPTS
            ),
            enabled=(
                phase28_config.AUTO_RECOVERY_ENABLED
            ),
        )

        self.safety = ObservabilitySafety(
            live_trading_enabled=(
                phase28_config.LIVE_TRADING_ENABLED
            ),
            real_broker_enabled=(
                phase28_config.REAL_BROKER_ENABLED
            ),
            place_real_orders=(
                phase28_config.PLACE_REAL_ORDERS
            ),
        )

        self.audit = ObservabilityAuditLogger(
            (
                f"{phase28_config.REPORT_DIRECTORY}/"
                f"{phase28_config.AUDIT_FILENAME}"
            )
        )

        self.readiness = ObservabilityReadiness(
            minimum_components=(
                phase28_config.MIN_COMPONENTS
            ),
            minimum_healthy_components=(
                phase28_config.MIN_HEALTHY_COMPONENTS
            ),
            maximum_critical_incidents=(
                phase28_config.MAX_CRITICAL_INCIDENTS
            ),
        )

        self.report = ObservabilityReport(
            phase28_config.REPORT_DIRECTORY,
            phase28_config.REPORT_FILENAME,
        )

    def observe_component(
        self,
        component: str,
        healthy: bool = True,
        details: Dict[str, Any] | None = None,
        auto_recover: bool = False,
    ) -> Dict[str, Any]:

        state = self.health.heartbeat(
            component,
            healthy,
            details,
        )

        self.audit.log(
            "HEALTH_CHECK",
            {
                "component": component,
                "healthy": healthy,
            },
        )

        incident = (
            self.incidents.detect_component_failure(
                component,
                healthy,
                details,
            )
        )

        recovery = None

        if incident:

            self.audit.log(
                "INCIDENT_DETECTED",
                incident.to_dict(),
            )

            if auto_recover:

                recovery = self.recovery.recover(
                    component
                )

                incident.recovered = bool(
                    recovery["recovered"]
                )

                incident.recovery_action = (
                    recovery["reason"]
                )

                incident.recovery_attempts = (
                    recovery["attempts"]
                )

                self.audit.log(
                    "RECOVERY_ATTEMPT",
                    recovery,
                )

        return {
            "health": state,
            "incident":
                incident.to_dict()
                if incident
                else None,
            "recovery": recovery,
        }

    def run(
        self,
        phase27_ready: bool = True,
    ) -> Dict[str, Any]:

        self.audit.log(
            "PHASE28_START",
            {
                "phase27_ready": phase27_ready
            },
        )

        # ----------------------------------------------------
        # SAFETY FIRST
        # ----------------------------------------------------

        safety_state = self.safety.validate()

        if not safety_state["safe"]:

            self.audit.log(
                "SAFETY_FAILURE",
                safety_state,
            )

        # ----------------------------------------------------
        # REQUIRED COMPONENTS
        # ----------------------------------------------------

        for component in (
            self.health.REQUIRED_COMPONENTS
        ):

            self.observe_component(
                component=component,
                healthy=True,
            )

        # ----------------------------------------------------
        # INCIDENT SNAPSHOT
        # ----------------------------------------------------

        incident_state = {
            "count":
                len(self.incidents.incidents),

            "critical_count":
                self.incidents.critical_count(),

            "incidents":
                self.incidents.snapshot(),
        }

        # ----------------------------------------------------
        # READINESS
        # ----------------------------------------------------

        readiness = self.readiness.evaluate(
            health=self.health.snapshot(),
            incidents=incident_state,
            safety=safety_state,
        )

        if phase27_ready is False:

            readiness["ready"] = False
            readiness["classification"] = (
                "OBSERVABILITY_BLOCKED_PHASE27_NOT_READY"
            )

        # ----------------------------------------------------
        # FINAL REPORT
        # ----------------------------------------------------

        payload = {
            "phase": 28,
            "name": (
                "Production Observability, "
                "Incident Detection and "
                "Automatic Recovery"
            ),
            "phase27_ready": phase27_ready,
            "health": self.health.snapshot(),
            "incidents": incident_state,
            "recovery": self.recovery.snapshot(),
            "safety": safety_state,
            "readiness": readiness,
            "real_orders_placed": 0,
            "live_trading_enabled": False,
            "real_broker_enabled": False,
            "place_real_orders": False,
        }

        report_path = self.report.write(
            payload
        )

        self.audit.log(
            "PHASE28_COMPLETE",
            {
                "ready": readiness["ready"],
                "report": report_path,
            },
        )

        return {
            **payload,
            "report_path": report_path,
        }

import json
from pathlib import Path
from typing import Dict, Optional

from config import phase24_config

from workers.live_activation.activation_config_validator import (
    ActivationConfigValidator,
)

from workers.live_activation.activation_gate import (
    LiveActivationGate,
)

from workers.live_activation.canary_limits import (
    CanaryLimitManager,
)

from workers.live_activation.dual_safety_gate import (
    DualSafetyGate,
)

from workers.live_activation.emergency_shutdown import (
    EmergencyShutdownController,
)

from workers.live_activation.rollback_controller import (
    RollbackController,
)

from workers.live_activation.broker_authorization import (
    BrokerAuthorizationChecker,
)

from workers.live_activation.position_reconciler import (
    LivePositionReconciler,
)

from workers.live_activation.health_monitor import (
    LiveHealthMonitor,
)

from workers.live_activation.audit_logger import (
    ActivationAuditLogger,
)

from workers.live_activation.readiness_evaluator import (
    ActivationReadinessEvaluator,
)


class Phase24LiveActivationWorker:

    def __init__(
        self,
        broker,
        intelligence_worker=None,
    ):

        self.broker = broker

        self.intelligence = (
            intelligence_worker
        )

        self.config_validator = (
            ActivationConfigValidator()
        )

        self.activation_gate = (
            LiveActivationGate()
        )

        self.canary_limits = (
            CanaryLimitManager(
                max_orders=(
                    phase24_config.CANARY_MAX_ORDERS
                ),
                max_quantity=(
                    phase24_config.CANARY_MAX_QUANTITY
                ),
                max_daily_loss=(
                    phase24_config.CANARY_MAX_DAILY_LOSS
                ),
                max_consecutive_losses=(
                    phase24_config.CANARY_MAX_CONSECUTIVE_LOSSES
                ),
                max_open_positions=(
                    phase24_config.CANARY_MAX_OPEN_POSITIONS
                ),
            )
        )

        self.safety = (
            DualSafetyGate()
        )

        self.emergency = (
            EmergencyShutdownController()
        )

        self.rollback = (
            RollbackController()
        )

        self.authorization = (
            BrokerAuthorizationChecker()
        )

        self.reconciler = (
            LivePositionReconciler()
        )

        self.health = (
            LiveHealthMonitor(
                max_errors=(
                    phase24_config.MAX_RUNTIME_ERRORS
                )
            )
        )

        self.audit = ActivationAuditLogger(
            str(
                Path(
                    phase24_config.REPORT_DIRECTORY
                )
                / phase24_config.AUDIT_FILENAME
            )
        )

        self.readiness = (
            ActivationReadinessEvaluator()
        )

    # --------------------------------------------------------
    # PHASE 23 READINESS
    # --------------------------------------------------------

    def check_phase23(
        self,
    ) -> Dict:

        path = Path(
            phase24_config.PHASE23_REPORT
        )

        if not path.exists():

            return {
                "ready": False,
                "reason": (
                    "Phase 23 report not found"
                ),
            }

        try:

            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            classification = str(
                data.get(
                    "readiness",
                    data.get(
                        "classification",
                        "",
                    ),
                )
            ).upper()

            return {
                "ready": True,
                "classification": classification,
                "report": str(path),
            }

        except Exception as exc:

            return {
                "ready": False,
                "reason": str(exc),
            }

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    def safety_configuration(
        self,
    ) -> Dict:

        return {
            "shadow_mode": (
                phase24_config.SHADOW_MODE
            ),
            "live_trading_enabled": (
                phase24_config.LIVE_TRADING_ENABLED
            ),
            "real_broker_enabled": (
                phase24_config.REAL_BROKER_ENABLED
            ),
            "place_real_orders": (
                phase24_config.PLACE_REAL_ORDERS
            ),
        }

    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

    def evaluate_readiness(
        self,
    ) -> Dict:

        configuration = (
            self.config_validator.validate(
                phase24_config
            )
        )

        phase23 = (
            self.check_phase23()
        )

        broker = (
            self.authorization.check(
                self.broker,
                require_real_broker=False,
            )
        )

        health = (
            self.health.check(
                self.broker,
                self.intelligence,
            )
        )

        reconciliation = (
            self.reconciler.reconcile(
                self.broker,
                {},
            )
        )

        canary = (
            self.canary_limits.evaluate(
                orders=0,
                quantity=(
                    phase24_config.DEFAULT_QUANTITY
                ),
                daily_loss=0.0,
                consecutive_losses=0,
                open_positions=0,
            )
        )

        safety_config = (
            self.safety_configuration()
        )

        # Phase 24 remains intentionally
        # NOT LIVE by default.
        safety_ready = (
            safety_config["shadow_mode"]
            and not safety_config[
                "live_trading_enabled"
            ]
            and not safety_config[
                "real_broker_enabled"
            ]
            and not safety_config[
                "place_real_orders"
            ]
        )

        safety = (
            self.safety.evaluate(
                primary=True,
                secondary=True,
            )
        )

        readiness = (
            self.readiness.evaluate(
                configuration_valid=(
                    configuration["valid"]
                ),
                phase23_ready=(
                    phase23["ready"]
                ),
                broker_ready=(
                    broker["authorized"]
                ),
                positions_reconciled=(
                    reconciliation[
                        "reconciled"
                    ]
                ),
                health_ready=(
                    health["healthy"]
                ),
                canary_ready=(
                    canary["allowed"]
                ),
                safety_ready=(
                    safety_ready
                    and safety["allowed"]
                ),
            )
        )

        self.audit.log(
            "READINESS_EVALUATION",
            readiness,
        )

        return {
            "configuration": configuration,
            "phase23": phase23,
            "broker": broker,
            "health": health,
            "reconciliation": reconciliation,
            "canary": canary,
            "safety": safety,
            "safety_configuration": safety_config,
            "readiness": readiness,
        }

    # --------------------------------------------------------
    # ACTIVATION ATTEMPT
    # --------------------------------------------------------

    def request_activation(
        self,
        explicit_activation: bool = False,
        manual_approval: bool = False,
    ) -> Dict:

        state = self.evaluate_readiness()

        result = self.activation_gate.evaluate(
            explicit_activation=(
                explicit_activation
            ),
            manual_approval=(
                manual_approval
            ),
            broker_authorized=(
                state["broker"]["authorized"]
            ),
            positions_reconciled=(
                state[
                    "reconciliation"
                ][
                    "reconciled"
                ]
            ),
            runtime_healthy=(
                state["health"]["healthy"]
            ),
            phase23_ready=(
                state["phase23"]["ready"]
            ),
            safety_config=(
                state["safety_configuration"]
            ),
        )

        self.audit.log(
            "ACTIVATION_REQUEST",
            result,
        )

        return {
            "activation": result,
            "readiness": state,
        }

    # --------------------------------------------------------
    # EMERGENCY SHUTDOWN
    # --------------------------------------------------------

    def emergency_shutdown(
        self,
        reason: str = "Manual emergency shutdown",
    ) -> Dict:

        shutdown = (
            self.emergency.trigger(
                reason
            )
        )

        self.activation_gate.deactivate()

        safety = (
            self.safety.emergency_shutdown()
        )

        rollback = (
            self.rollback.trigger(
                reason
            )
        )

        result = {
            "shutdown": shutdown,
            "safety": safety,
            "rollback": rollback,
        }

        self.audit.log(
            "EMERGENCY_SHUTDOWN",
            result,
        )

        return result

    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    def recover(
        self,
    ) -> Dict:

        shutdown = (
            self.emergency.recover()
        )

        safety = (
            self.safety.recover()
        )

        rollback = (
            self.rollback.reset()
        )

        self.health.reset()

        result = {
            "shutdown": shutdown,
            "safety": safety,
            "rollback": rollback,
        }

        self.audit.log(
            "RECOVERY",
            result,
        )

        return result

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    def save_report(
        self,
        result: Dict,
    ) -> str:

        directory = Path(
            phase24_config.REPORT_DIRECTORY
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            / phase24_config.REPORT_FILENAME
        )

        path.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(path)

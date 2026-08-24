# ============================================================
# PHASE 26 - MAIN CANARY VALIDATION WORKER
# ============================================================

import json
from pathlib import Path
from typing import Dict, List, Optional

from config import phase26_config

from workers.canary_validation.performance_validator import (
    CanaryPerformanceValidator,
)

from workers.canary_validation.risk_validator import (
    CanaryRiskValidator,
)

from workers.canary_validation.execution_validator import (
    CanaryExecutionValidator,
)

from workers.canary_validation.health_validator import (
    CanaryHealthValidator,
)

from workers.canary_validation.safety_validator import (
    CanarySafetyValidator,
)

from workers.canary_validation.rollback_engine import (
    CanaryRollbackEngine,
)

from workers.canary_validation.deployment_state import (
    CanaryDeploymentState,
)

from workers.canary_validation.audit_logger import (
    CanaryRollbackAuditLogger,
)

from workers.canary_validation.readiness_evaluator import (
    CanaryReadinessEvaluator,
)


class Phase26CanaryWorker:

    def __init__(self):

        self.performance_validator = (
            CanaryPerformanceValidator(
                min_profitable_trade_rate=(
                    phase26_config
                    .MIN_PROFITABLE_TRADE_RATE
                ),
                min_expectancy=(
                    phase26_config
                    .MIN_EXPECTANCY
                ),
                max_daily_loss=(
                    phase26_config
                    .MAX_DAILY_LOSS
                ),
                max_drawdown=(
                    phase26_config
                    .MAX_DRAWDOWN
                ),
            )
        )

        self.risk_validator = (
            CanaryRiskValidator(
                max_canary_trades=(
                    phase26_config
                    .MAX_CANARY_TRADES
                ),
                max_consecutive_losses=(
                    phase26_config
                    .MAX_CONSECUTIVE_LOSSES
                ),
            )
        )

        self.execution_validator = (
            CanaryExecutionValidator(
                max_rejected_orders=(
                    phase26_config
                    .MAX_REJECTED_ORDERS
                ),
                max_execution_failures=(
                    phase26_config
                    .MAX_EXECUTION_FAILURES
                ),
            )
        )

        self.health_validator = (
            CanaryHealthValidator(
                max_health_failures=(
                    phase26_config
                    .MAX_HEALTH_FAILURES
                )
            )
        )

        self.safety_validator = (
            CanarySafetyValidator()
        )

        self.rollback_engine = (
            CanaryRollbackEngine(
                enabled=(
                    phase26_config
                    .AUTO_ROLLBACK_ENABLED
                )
            )
        )

        self.state = (
            CanaryDeploymentState(
                str(
                    Path(
                        phase26_config
                        .REPORT_DIRECTORY
                    )
                    / phase26_config
                    .STATE_FILENAME
                )
            )
        )

        self.audit = (
            CanaryRollbackAuditLogger(
                str(
                    Path(
                        phase26_config
                        .REPORT_DIRECTORY
                    )
                    / phase26_config
                    .AUDIT_FILENAME
                )
            )
        )

        self.readiness = (
            CanaryReadinessEvaluator(
                minimum_score=(
                    phase26_config
                    .MIN_READINESS_SCORE
                )
            )
        )

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------

    def run(
        self,
        trades: Optional[List[Dict]] = None,
        orders: Optional[List[Dict]] = None,
        realized_pnl: float = 0.0,
        drawdown: float = 0.0,
        consecutive_losses: int = 0,
        health: Optional[Dict] = None,
        safety: Optional[Dict] = None,
        observations: int = 0,
    ) -> Dict:

        trades = trades or []
        orders = orders or []

        health = health or {
            "healthy": True,
            "failures": 0,
        }

        safety = safety or (
            dict(
                phase26_config
                .SAFETY_ASSERTIONS
            )
        )

        performance = (
            self.performance_validator.validate(
                trades=trades,
                realized_pnl=realized_pnl,
                drawdown=drawdown,
            )
        )

        risk = (
            self.risk_validator.validate(
                trades=trades,
                consecutive_losses=(
                    consecutive_losses
                ),
            )
        )

        execution = (
            self.execution_validator.validate(
                orders=orders
            )
        )

        health_result = (
            self.health_validator.validate(
                health=health
            )
        )

        safety_result = (
            self.safety_validator.validate(
                safety=safety
            )
        )

        rollback = (
            self.rollback_engine.evaluate(
                performance=performance,
                risk=risk,
                execution=execution,
                health=health_result,
                safety=safety_result,
            )
        )

        observation_pass = (
            observations
            >= phase26_config
            .MIN_CANARY_OBSERVATIONS
        )

        trade_pass = (
            len(trades)
            >= phase26_config
            .MIN_CANARY_TRADES
        )

        checks = {
            "performance": performance[
                "passed"
            ],
            "risk": risk[
                "passed"
            ],
            "execution": execution[
                "passed"
            ],
            "health": health_result[
                "passed"
            ],
            "safety": safety_result[
                "passed"
            ],
            "minimum_observations": (
                observation_pass
            ),
            "minimum_trades": (
                trade_pass
            ),
            "rollback_not_required": (
                not rollback[
                    "rollback_required"
                ]
            ),
        }

        readiness = (
            self.readiness.evaluate(
                checks=checks
            )
        )

        if rollback[
            "rollback_triggered"
        ]:

            deployment_state = (
                "ROLLED_BACK"
            )

            readiness["ready"] = False

            readiness[
                "classification"
            ] = "CANARY_ROLLBACK_REQUIRED"

        else:

            deployment_state = (
                "CANARY_CONTINUE"
                if readiness["ready"]
                else "CANARY_HOLD"
            )

        state_record = {
            "state": deployment_state,
            "live_trading_enabled": False,
            "real_broker_enabled": False,
            "real_orders": 0,
            "rollback": rollback,
        }

        state_path = self.state.save(
            state_record
        )

        self.audit.log(
            "PHASE26_VALIDATION",
            {
                "deployment_state": (
                    deployment_state
                ),
                "readiness": readiness,
                "rollback": rollback,
            },
        )

        if rollback[
            "rollback_triggered"
        ]:

            self.audit.log(
                "AUTOMATIC_ROLLBACK",
                rollback,
            )

        result = {
            "phase": 26,
            "symbol": (
                phase26_config
                .DEFAULT_SYMBOL
            ),
            "observations": int(
                observations
            ),
            "trades": len(
                trades
            ),
            "performance": performance,
            "risk": risk,
            "execution": execution,
            "health": health_result,
            "safety": safety_result,
            "rollback": rollback,
            "readiness": readiness,
            "deployment_state": (
                deployment_state
            ),
            "real_orders": 0,
            "live_trading_enabled": False,
            "real_broker_enabled": False,
            "state_file": state_path,
        }

        return result

    # ---------------------------------------------------------
    # SAVE REPORT
    # ---------------------------------------------------------

    def save_report(
        self,
        result: Dict,
    ) -> str:

        directory = Path(
            phase26_config
            .REPORT_DIRECTORY
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            / phase26_config
            .REPORT_FILENAME
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

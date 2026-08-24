import json
from pathlib import Path
from typing import Dict

from config.phase22_config import (
    DEFAULT_QUANTITY,
    DEFAULT_SYMBOL,
    REPORT_DIRECTORY,
    REPORT_FILENAME,
)

from workers.deployment.deployment_config_validator import (
    DeploymentConfigValidator,
)

from workers.deployment.deployment_gate import (
    DeploymentGate,
)

from workers.deployment.deployment_health_monitor import (
    DeploymentHealthMonitor,
)

from workers.deployment.deployment_limits import (
    DeploymentLimits,
)

from workers.deployment.deployment_readiness import (
    DeploymentReadinessEvaluator,
)

from workers.deployment.deployment_audit_logger import (
    DeploymentAuditLogger,
)

from workers.deployment.live_trading_gate import (
    LiveTradingGate,
)

from config.phase22_config import (
    MAX_ORDER_QUANTITY,
    MAX_DAILY_TRADES,
    MAX_DAILY_LOSS,
)


class Phase22DeploymentWorker:

    def __init__(
        self,
        broker,
        intelligence_worker,
        initial_capital: float = 100000.0,
    ):

        self.broker = broker

        self.intelligence = (
            intelligence_worker
        )

        self.initial_capital = float(
            initial_capital
        )

        self.config_validator = (
            DeploymentConfigValidator()
        )

        self.deployment_gate = (
            DeploymentGate()
        )

        self.live_gate = (
            LiveTradingGate()
        )

        self.health_monitor = (
            DeploymentHealthMonitor()
        )

        self.limits = DeploymentLimits(
            max_order_quantity=MAX_ORDER_QUANTITY,
            max_daily_trades=MAX_DAILY_TRADES,
            max_daily_loss=MAX_DAILY_LOSS,
        )

        self.readiness = (
            DeploymentReadinessEvaluator()
        )

        self.audit = (
            DeploymentAuditLogger()
        )

    def run(
        self,
        symbol: str = DEFAULT_SYMBOL,
        quantity: int = DEFAULT_QUANTITY,
    ) -> Dict:

        self.audit.log(
            "PHASE22_START",
            {
                "symbol": symbol,
                "quantity": quantity,
            },
        )

        config = (
            self.config_validator.validate()
        )

        config_ok = bool(
            config["valid"]
        )

        self.audit.log(
            "CONFIG_VALIDATION",
            config,
        )

        deployment = (
            self.deployment_gate.open(
                config
            )
        )

        deployment_ok = bool(
            deployment["allowed"]
        )

        health = (
            self.health_monitor.check(
                broker=self.broker,
                intelligence_worker=(
                    self.intelligence
                ),
            )
        )

        health_ok = bool(
            health["healthy"]
        )

        order_limit = (
            self.limits.validate_order(
                quantity
            )
        )

        order_ok = bool(
            order_limit["allowed"]
        )

        live = (
            self.live_gate.evaluate()
        )

        live_disabled = (
            not live["allowed"]
        )

        checks = {
            "configuration_valid": config_ok,
            "deployment_gate": deployment_ok,
            "broker_healthy": health_ok,
            "order_limits_valid": order_ok,
            "live_trading_blocked": live_disabled,
        }

        result = (
            self.readiness.evaluate(
                checks
            )
        )

        report = {
            "phase": 22,
            "name": (
                "Controlled Deployment "
                "and Live Trading Gate"
            ),
            "symbol": symbol,
            "quantity": quantity,
            "environment": config[
                "environment"
            ],
            "configuration": config,
            "deployment_gate": deployment,
            "health": health,
            "order_limit": order_limit,
            "live_gate": live,
            "readiness": result,
            "real_orders_placed": 0,
            "safety": {
                "paper_only": True,
                "live_trading_enabled": (
                    config[
                        "live_trading_enabled"
                    ]
                ),
                "real_broker_enabled": (
                    config[
                        "real_broker_enabled"
                    ]
                ),
                "real_orders_placed": 0,
            },
        }

        self.save_report(report)

        self.audit.log(
            "PHASE22_COMPLETE",
            {
                "ready": result["ready"],
                "score": result["score"],
            },
        )

        return report

    def save_report(
        self,
        result: Dict,
    ) -> str:

        directory = Path(
            REPORT_DIRECTORY
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            / REPORT_FILENAME
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

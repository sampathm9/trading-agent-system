import json
from pathlib import Path
from typing import Dict


class Phase25CanaryWorker:

    def __init__(
        self,
        broker,
        intelligence_worker,
        config,
    ):

        from .canary_limits import CanaryLimits
        from .canary_safety import CanarySafety
        from .canary_audit_logger import (
            CanaryAuditLogger,
        )
        from .canary_health_monitor import (
            CanaryHealthMonitor,
        )
        from .canary_alert_engine import (
            CanaryAlertEngine,
        )
        from .canary_readiness import (
            CanaryReadiness,
        )

        self.broker = broker
        self.intelligence = intelligence_worker
        self.config = config

        self.limits = CanaryLimits(
            max_trades=config.MAX_CANARY_TRADES,
            max_consecutive_losses=(
                config.MAX_CONSECUTIVE_LOSSES
            ),
            max_daily_loss=(
                config.MAX_DAILY_LOSS
            ),
            max_daily_profit=(
                config.MAX_DAILY_PROFIT
            ),
            max_position_quantity=(
                config.MAX_POSITION_QUANTITY
            ),
        )

        self.safety = CanarySafety()
        self.audit = CanaryAuditLogger()
        self.health = CanaryHealthMonitor()
        self.alerts = CanaryAlertEngine()
        self.readiness = CanaryReadiness()

        self.observations = []

    def observe(
        self,
        candle: Dict,
        signal: Dict,
    ):

        observation = {
            "candle": candle,
            "signal": signal,
            "real_order_placed": False,
            "live_execution": False,
        }

        self.observations.append(
            observation
        )

        self.audit.log(
            "MARKET_OBSERVATION",
            observation,
        )

        return observation

    def run(
        self,
        candles,
    ) -> Dict:

        safety = self.safety.can_operate(
            self.config
        )

        if not safety["allowed"]:
            self.audit.log(
                "CANARY_BLOCKED",
                safety,
            )

            return {
                "status": "BLOCKED",
                "safety": safety,
                "observations": [],
            }

        history = []

        for candle in candles:

            history.append(candle)

            if len(history) < 3:
                continue

            signal = self.intelligence.strategy_signal(
                candles=history,
                news=None,
            )

            self.observe(
                candle=candle,
                signal=signal,
            )

        broker_connected = bool(
            self.broker.is_connected()
        )

        health = self.health.evaluate(
            broker_connected=broker_connected,
            intelligence_healthy=True,
            position_reconciliation=True,
            safety_healthy=True,
            audit_healthy=True,
        )

        limit_result = self.limits.check(
            total_trades=0,
            realized_pnl=0.0,
            consecutive_losses=0,
            position_quantity=0,
        )

        alert_result = self.alerts.evaluate(
            limits=limit_result,
            health=health,
            safety=safety,
        )

        readiness = self.readiness.evaluate(
            config_safe=safety["allowed"],
            health_score=health["score"],
            broker_connected=broker_connected,
            reconciliation=True,
            alerts_clear=(
                alert_result["alert_count"] == 0
            ),
            observation_count=len(
                self.observations
            ),
        )

        self.audit.log(
            "CANARY_READINESS",
            readiness,
        )

        return {
            "status": "COMPLETED",
            "observations": self.observations,
            "health": health,
            "limits": limit_result,
            "alerts": alert_result,
            "safety": safety,
            "readiness": readiness,
            "real_orders_placed": 0,
        }

    def save_report(
        self,
        result: Dict,
    ) -> str:

        directory = Path(
            self.config.REPORT_DIRECTORY
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            / self.config.REPORT_FILENAME
        )

        path.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        self.audit.export(
            str(
                directory
                / self.config.AUDIT_FILENAME
            )
        )

        return str(path)

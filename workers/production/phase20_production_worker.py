import json
from pathlib import Path
from typing import Dict


class Phase20ProductionWorker:

    def __init__(
        self,
        preflight_validator,
        runtime_safety,
        health_monitor,
        audit_logger,
        readiness_evaluator,
        report_directory: str,
        report_filename: str,
    ):

        self.preflight = (
            preflight_validator
        )

        self.safety = (
            runtime_safety
        )

        self.health = (
            health_monitor
        )

        self.audit = (
            audit_logger
        )

        self.evaluator = (
            readiness_evaluator
        )

        self.report_directory = Path(
            report_directory
        )

        self.report_filename = (
            report_filename
        )

    def run(
        self,
        broker,
        intelligence,
        candles,
    ) -> Dict:

        self.audit.log(
            "PHASE20_START",
            {
                "candles": len(candles),
            },
        )

        preflight = (
            self.preflight.validate(
                broker=broker,
                intelligence=intelligence,
                candles=candles,
            )
        )

        self.health.heartbeat(
            "broker"
        )

        self.health.heartbeat(
            "intelligence"
        )

        self.health.heartbeat(
            "historical_data"
        )

        safety = self.safety.can_trade(
            quantity=1,
            trade_count=0,
            realized_pnl=0.0,
            mode="PAPER",
        )

        self.audit.log(
            "SAFETY_CHECK",
            safety,
        )

        health = (
            self.health.snapshot()
        )

        audit_events = len(
            self.audit.read_events()
        )

        readiness = (
            self.evaluator.evaluate(
                preflight=preflight,
                safety=safety,
                health=health,
                audit_events=audit_events,
            )
        )

        self.audit.log(
            "READINESS_RESULT",
            readiness,
        )

        result = {
            "phase": 20,
            "name": (
                "Production Readiness "
                "& Deployment Safety"
            ),
            "preflight": preflight,
            "safety": safety,
            "health": health,
            "audit_events": audit_events,
            "readiness": readiness,
            "real_orders_placed": 0,
        }

        self.save_report(
            result
        )

        return result

    def save_report(
        self,
        result: Dict,
    ) -> str:

        self.report_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            self.report_directory
            / self.report_filename
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

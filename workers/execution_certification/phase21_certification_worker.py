import json
from pathlib import Path
from typing import Dict


class Phase21CertificationWorker:

    def __init__(
        self,
        config,
        execution_gate,
        reconciler,
        audit,
        kill_switch,
        report_directory,
        report_filename,
    ):

        self.config = config

        self.execution_gate = (
            execution_gate
        )

        self.reconciler = (
            reconciler
        )

        self.audit = audit

        self.kill_switch = (
            kill_switch
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
    ) -> Dict:

        self.audit.record(
            "PHASE21_START",
            {
                "runtime_mode": (
                    self.config.RUNTIME_MODE
                ),
            },
        )

        # -----------------------------------------------------
        # BROKER HEALTH
        # -----------------------------------------------------

        health = (
            self.execution_gate
            .broker_health
            .check(broker)
        )

        # -----------------------------------------------------
        # POSITION RECONCILIATION
        # -----------------------------------------------------

        broker_positions = (
            broker.get_positions()
        )

        reconciliation = (
            self.reconciler.reconcile(
                broker_positions=(
                    broker_positions
                ),
                expected_positions={},
            )
        )

        self.audit.record(
            "POSITION_RECONCILIATION",
            reconciliation,
        )

        # -----------------------------------------------------
        # EXECUTION CERTIFICATION
        # -----------------------------------------------------

        authorization = (
            self.execution_gate.authorize(
                broker=broker,
                symbol=self.config.DEFAULT_SYMBOL,
                quantity=self.config.DEFAULT_QUANTITY,
                price=100.0,
                side="BUY",
                idempotency_key=(
                    "PHASE21_CERTIFICATION_001"
                ),
                trade_count=0,
                realized_pnl=0.0,
            )
        )

        self.audit.record(
            "EXECUTION_GATE_CHECK",
            authorization,
        )

        # IMPORTANT:
        # The certification checks the gate.
        # It DOES NOT place an order.

        real_orders_placed = 0

        report = {
            "phase": 21,
            "name": (
                "Broker Execution Certification "
                "& Kill-Switch Layer"
            ),
            "runtime_mode": (
                self.config.RUNTIME_MODE
            ),
            "live_trading_enabled": (
                self.config.ALLOW_LIVE_TRADING
            ),
            "real_broker_orders_enabled": (
                self.config.ALLOW_REAL_BROKER_ORDERS
            ),
            "live_broker_enabled": (
                self.config.LIVE_BROKER_ENABLED
            ),
            "broker_health": health,
            "position_reconciliation": (
                reconciliation
            ),
            "execution_gate": authorization,
            "kill_switch": (
                self.kill_switch.status()
            ),
            "real_orders_placed": (
                real_orders_placed
            ),
            "certified": (
                health["healthy"]
                and reconciliation["reconciled"]
                and authorization["authorized"]
                and real_orders_placed == 0
                and self.config.ALLOW_LIVE_TRADING
                is False
                and self.config.ALLOW_REAL_BROKER_ORDERS
                is False
                and self.config.LIVE_BROKER_ENABLED
                is False
            ),
        }

        self.save_report(
            report
        )

        self.audit.record(
            "PHASE21_COMPLETE",
            report,
        )

        return report

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

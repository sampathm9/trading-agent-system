from typing import Dict


class Phase20PreflightValidator:

    def __init__(
        self,
        config_module,
    ):
        self.config = config_module

    def validate_configuration(self) -> Dict:

        checks = []

        checks.append({
            "name": "runtime_mode",
            "passed": self.config.RUNTIME_MODE == "PAPER",
            "value": self.config.RUNTIME_MODE,
        })

        checks.append({
            "name": "live_trading_disabled",
            "passed": (
                self.config.ALLOW_LIVE_TRADING
                is False
            ),
            "value": self.config.ALLOW_LIVE_TRADING,
        })

        checks.append({
            "name": "real_orders_disabled",
            "passed": (
                self.config.ALLOW_REAL_BROKER_ORDERS
                is False
            ),
            "value": (
                self.config.ALLOW_REAL_BROKER_ORDERS
            ),
        })

        checks.append({
            "name": "quantity_limit",
            "passed": (
                self.config.DEFAULT_QUANTITY > 0
                and self.config.MAX_QUANTITY >=
                self.config.DEFAULT_QUANTITY
            ),
            "value": self.config.MAX_QUANTITY,
        })

        checks.append({
            "name": "trade_limit",
            "passed": (
                self.config.MAX_TRADES_PER_SESSION > 0
            ),
            "value": (
                self.config.MAX_TRADES_PER_SESSION
            ),
        })

        checks.append({
            "name": "loss_limit",
            "passed": (
                self.config.MAX_SESSION_LOSS > 0
            ),
            "value": self.config.MAX_SESSION_LOSS,
        })

        passed = all(
            check["passed"]
            for check in checks
        )

        return {
            "passed": passed,
            "checks": checks,
        }

    def validate_dependencies(
        self,
        broker,
        intelligence,
    ) -> Dict:

        checks = []

        checks.append({
            "name": "broker_available",
            "passed": broker is not None,
        })

        checks.append({
            "name": "intelligence_available",
            "passed": intelligence is not None,
        })

        checks.append({
            "name": "broker_connected",
            "passed": bool(
                broker.is_connected()
            ),
        })

        passed = all(
            check["passed"]
            for check in checks
        )

        return {
            "passed": passed,
            "checks": checks,
        }

    def validate_historical_data(
        self,
        candles,
    ) -> Dict:

        count = len(candles)

        passed = count >= 3

        return {
            "passed": passed,
            "candle_count": count,
            "minimum_required": 3,
        }

    def validate(
        self,
        broker,
        intelligence,
        candles,
    ) -> Dict:

        configuration = (
            self.validate_configuration()
        )

        dependencies = (
            self.validate_dependencies(
                broker,
                intelligence,
            )
        )

        historical_data = (
            self.validate_historical_data(
                candles
            )
        )

        passed = all([
            configuration["passed"],
            dependencies["passed"],
            historical_data["passed"],
        ])

        return {
            "passed": passed,
            "configuration": configuration,
            "dependencies": dependencies,
            "historical_data": historical_data,
        }

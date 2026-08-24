from typing import Dict


class Phase21ExecutionGate:

    def __init__(
        self,
        config,
        order_validator,
        idempotency_guard,
        kill_switch,
        broker_health,
    ):

        self.config = config

        self.order_validator = (
            order_validator
        )

        self.idempotency = (
            idempotency_guard
        )

        self.kill_switch = (
            kill_switch
        )

        self.broker_health = (
            broker_health
        )

    def authorize(
        self,
        broker,
        symbol: str,
        quantity: int,
        price: float,
        side: str,
        idempotency_key: str,
        trade_count: int = 0,
        realized_pnl: float = 0.0,
    ) -> Dict:

        checks = []

        # -----------------------------------------------------
        # MODE
        # -----------------------------------------------------

        mode_passed = (
            self.config.RUNTIME_MODE
            == "PAPER"
        )

        checks.append({
            "name": "paper_mode",
            "passed": mode_passed,
        })

        if not mode_passed:

            return {
                "authorized": False,
                "reason": (
                    "Phase 21 requires PAPER mode."
                ),
                "checks": checks,
            }

        # -----------------------------------------------------
        # LIVE SAFETY
        # -----------------------------------------------------

        live_disabled = (
            self.config.ALLOW_LIVE_TRADING
            is False
            and
            self.config.ALLOW_REAL_BROKER_ORDERS
            is False
            and
            self.config.LIVE_BROKER_ENABLED
            is False
        )

        checks.append({
            "name": "live_execution_disabled",
            "passed": live_disabled,
        })

        if not live_disabled:

            return {
                "authorized": False,
                "reason": (
                    "Live execution flags are not "
                    "safely disabled."
                ),
                "checks": checks,
            }

        # -----------------------------------------------------
        # KILL SWITCH
        # -----------------------------------------------------

        kill = (
            self.kill_switch.can_execute()
        )

        checks.append({
            "name": "kill_switch",
            "passed": kill["allowed"],
        })

        if not kill["allowed"]:

            return {
                "authorized": False,
                "reason": kill["reason"],
                "checks": checks,
            }

        # -----------------------------------------------------
        # BROKER HEALTH
        # -----------------------------------------------------

        health = (
            self.broker_health.check(
                broker
            )
        )

        checks.append({
            "name": "broker_health",
            "passed": health["healthy"],
        })

        if (
            self.config.REQUIRE_BROKER_HEALTH
            and not health["healthy"]
        ):

            return {
                "authorized": False,
                "reason": health["reason"],
                "checks": checks,
            }

        # -----------------------------------------------------
        # ORDER VALIDATION
        # -----------------------------------------------------

        validation = (
            self.order_validator.validate(
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
            )
        )

        checks.append({
            "name": "order_validation",
            "passed": validation["passed"],
        })

        if not validation["passed"]:

            return {
                "authorized": False,
                "reason": (
                    "Order validation failed."
                ),
                "checks": checks,
                "order_validation": validation,
            }

        # -----------------------------------------------------
        # SESSION LIMITS
        # -----------------------------------------------------

        session_allowed = (
            trade_count
            < self.config.MAX_SESSION_TRADES
            and
            realized_pnl
            > -self.config.MAX_SESSION_LOSS
        )

        checks.append({
            "name": "session_limits",
            "passed": session_allowed,
        })

        if not session_allowed:

            return {
                "authorized": False,
                "reason": (
                    "Session trading limit reached."
                ),
                "checks": checks,
            }

        # -----------------------------------------------------
        # IDEMPOTENCY
        # -----------------------------------------------------

        duplicate = (
            self.idempotency.check(
                idempotency_key
            )
        )

        checks.append({
            "name": "idempotency",
            "passed": duplicate["allowed"],
        })

        if not duplicate["allowed"]:

            return {
                "authorized": False,
                "reason": duplicate["reason"],
                "checks": checks,
            }

        # -----------------------------------------------------
        # AUTHORIZED
        # -----------------------------------------------------

        self.idempotency.register(
            idempotency_key
        )

        return {
            "authorized": True,
            "reason": (
                "Execution gate passed."
            ),
            "checks": checks,
            "order_validation": validation,
        }

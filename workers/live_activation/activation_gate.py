from typing import Dict


class LiveActivationGate:

    def __init__(self):

        self.activated = False
        self.activation_attempts = 0

    def evaluate(
        self,
        explicit_activation: bool,
        manual_approval: bool,
        broker_authorized: bool,
        positions_reconciled: bool,
        runtime_healthy: bool,
        phase23_ready: bool,
        safety_config: Dict,
    ) -> Dict:

        self.activation_attempts += 1

        failures = []

        if not explicit_activation:
            failures.append(
                "Explicit activation not provided"
            )

        if not manual_approval:
            failures.append(
                "Manual approval not provided"
            )

        if not broker_authorized:
            failures.append(
                "Broker authorization failed"
            )

        if not positions_reconciled:
            failures.append(
                "Position reconciliation failed"
            )

        if not runtime_healthy:
            failures.append(
                "Runtime health check failed"
            )

        if not phase23_ready:
            failures.append(
                "Phase 23 shadow readiness failed"
            )

        if safety_config.get(
            "shadow_mode",
            True,
        ):
            failures.append(
                "Shadow mode is enabled"
            )

        if not safety_config.get(
            "live_trading_enabled",
            False,
        ):
            failures.append(
                "Live trading is disabled"
            )

        if not safety_config.get(
            "real_broker_enabled",
            False,
        ):
            failures.append(
                "Real broker is disabled"
            )

        if not safety_config.get(
            "place_real_orders",
            False,
        ):
            failures.append(
                "Real order placement is disabled"
            )

        allowed = len(failures) == 0

        self.activated = allowed

        return {
            "allowed": allowed,
            "activated": allowed,
            "attempt": self.activation_attempts,
            "failures": failures,
        }

    def deactivate(self):

        self.activated = False

        return {
            "activated": False,
            "reason": "Activation gate deactivated",
        }

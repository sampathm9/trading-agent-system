# ============================================================
# PHASE 26 - EXECUTION VALIDATOR
# ============================================================

from typing import Dict, List


class CanaryExecutionValidator:

    def __init__(
        self,
        max_rejected_orders: int,
        max_execution_failures: int,
    ):

        self.max_rejected_orders = int(
            max_rejected_orders
        )

        self.max_execution_failures = int(
            max_execution_failures
        )

    def validate(
        self,
        orders: List[Dict],
    ) -> Dict:

        rejected = 0
        failures = 0

        for order in orders:

            status = str(
                order.get(
                    "status",
                    "",
                )
            ).upper()

            if "REJECT" in status:
                rejected += 1

            if (
                "FAIL" in status
                or "ERROR" in status
            ):
                failures += 1

        rejection_pass = (
            rejected
            <= self.max_rejected_orders
        )

        failure_pass = (
            failures
            <= self.max_execution_failures
        )

        passed = (
            rejection_pass
            and failure_pass
        )

        return {
            "passed": bool(passed),
            "orders": len(orders),
            "rejected_orders": rejected,
            "execution_failures": failures,
            "checks": {
                "rejected_orders": bool(
                    rejection_pass
                ),
                "execution_failures": bool(
                    failure_pass
                ),
            },
        }

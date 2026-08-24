from typing import Dict


class Phase21OrderValidator:

    def __init__(
        self,
        max_quantity: int,
        max_order_value: float,
    ):

        self.max_quantity = int(
            max_quantity
        )

        self.max_order_value = float(
            max_order_value
        )

    def validate(
        self,
        symbol: str,
        quantity: int,
        price: float,
        side: str,
    ) -> Dict:

        checks = []

        symbol_valid = bool(
            str(symbol).strip()
        )

        checks.append({
            "name": "symbol",
            "passed": symbol_valid,
        })

        quantity_valid = (
            int(quantity) > 0
            and int(quantity)
            <= self.max_quantity
        )

        checks.append({
            "name": "quantity",
            "passed": quantity_valid,
            "value": int(quantity),
        })

        price_valid = (
            float(price) > 0
        )

        checks.append({
            "name": "price",
            "passed": price_valid,
            "value": float(price),
        })

        side_valid = str(side).upper() in {
            "BUY",
            "SELL",
        }

        checks.append({
            "name": "side",
            "passed": side_valid,
            "value": str(side).upper(),
        })

        order_value = (
            float(quantity)
            * float(price)
        )

        value_valid = (
            order_value
            <= self.max_order_value
        )

        checks.append({
            "name": "order_value",
            "passed": value_valid,
            "value": order_value,
        })

        passed = all(
            item["passed"]
            for item in checks
        )

        return {
            "passed": passed,
            "checks": checks,
            "order_value": order_value,
        }

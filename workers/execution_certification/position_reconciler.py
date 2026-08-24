from typing import Dict


class Phase21PositionReconciler:

    def reconcile(
        self,
        broker_positions: Dict,
        expected_positions: Dict,
    ) -> Dict:

        broker_positions = (
            broker_positions or {}
        )

        expected_positions = (
            expected_positions or {}
        )

        symbols = set(
            broker_positions
        ) | set(
            expected_positions
        )

        differences = []

        for symbol in sorted(
            symbols
        ):

            broker_position = (
                broker_positions.get(
                    symbol
                )
            )

            expected_position = (
                expected_positions.get(
                    symbol
                )
            )

            broker_quantity = (
                int(
                    broker_position.get(
                        "quantity",
                        0,
                    )
                )
                if broker_position
                else 0
            )

            expected_quantity = (
                int(
                    expected_position.get(
                        "quantity",
                        0,
                    )
                )
                if expected_position
                else 0
            )

            if (
                broker_quantity
                != expected_quantity
            ):

                differences.append({
                    "symbol": symbol,
                    "broker_quantity": (
                        broker_quantity
                    ),
                    "expected_quantity": (
                        expected_quantity
                    ),
                })

        return {
            "reconciled": (
                len(differences) == 0
            ),
            "differences": differences,
        }

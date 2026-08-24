from typing import Dict


class LivePositionReconciler:

    def reconcile(
        self,
        broker,
        expected_positions: Dict,
    ) -> Dict:

        actual_positions = (
            broker.get_positions()
        )

        mismatches = []

        symbols = set(
            expected_positions.keys()
        ) | set(
            actual_positions.keys()
        )

        for symbol in symbols:

            expected = expected_positions.get(
                symbol,
                0,
            )

            actual_data = (
                actual_positions.get(
                    symbol
                )
            )

            actual = (
                int(
                    actual_data.get(
                        "quantity",
                        0,
                    )
                )
                if actual_data
                else 0
            )

            if expected != actual:

                mismatches.append(
                    {
                        "symbol": symbol,
                        "expected": expected,
                        "actual": actual,
                    }
                )

        return {
            "reconciled": len(mismatches) == 0,
            "mismatches": mismatches,
            "actual_positions": actual_positions,
        }

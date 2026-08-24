from typing import Dict, List


class StressTester:

    # ---------------------------------------------------------
    # APPLY STRESS
    # ---------------------------------------------------------

    def apply(
        self,
        pnl_values: List[float],
        multiplier: float,
    ) -> List[float]:

        multiplier = float(
            multiplier
        )

        if multiplier < 0:
            raise ValueError(
                "Stress multiplier cannot be negative."
            )

        return [
            round(
                float(pnl) * multiplier,
                6,
            )
            for pnl in pnl_values
        ]

    # ---------------------------------------------------------
    # ANALYZE
    # ---------------------------------------------------------

    def analyze(
        self,
        pnl_values: List[float],
        multiplier: float,
    ) -> Dict:

        stressed = self.apply(
            pnl_values=pnl_values,
            multiplier=multiplier,
        )

        total_pnl = sum(
            stressed
        )

        profitable_cycles = sum(
            1
            for pnl in stressed
            if pnl > 0
        )

        total_cycles = len(
            stressed
        )

        profit_probability = (
            profitable_cycles
            / total_cycles
            if total_cycles
            else 0.0
        )

        worst_cycle = (
            min(stressed)
            if stressed
            else 0.0
        )

        return {
            "multiplier": multiplier,
            "stressed_pnl": stressed,
            "total_pnl": round(
                total_pnl,
                6,
            ),
            "profitable_cycles": (
                profitable_cycles
            ),
            "total_cycles": total_cycles,
            "profit_probability": round(
                profit_probability,
                6,
            ),
            "worst_cycle_pnl": round(
                worst_cycle,
                6,
            ),
        }

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------

    def run(
        self,
        pnl_values: List[float],
        multipliers: List[float],
    ) -> List[Dict]:

        if not pnl_values:
            raise ValueError(
                "Stress testing requires P&L values."
            )

        if not multipliers:
            raise ValueError(
                "Stress testing requires multipliers."
            )

        return [
            self.analyze(
                pnl_values=pnl_values,
                multiplier=multiplier,
            )
            for multiplier in multipliers
        ]
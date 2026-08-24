from typing import Dict, List

from config.phase18_config import (
    MAX_ACCEPTABLE_DRAWDOWN,
    MIN_PROFIT_PROBABILITY,
    MIN_ROBUSTNESS_SCORE,
)


class RobustnessAnalyzer:

    # ---------------------------------------------------------
    # SCORE
    # ---------------------------------------------------------

    def calculate_score(
        self,
        monte_carlo: Dict,
        stress_tests: List[Dict],
    ) -> float:

        probability = float(
            monte_carlo.get(
                "probability_of_profit",
                0.0,
            )
        )

        worst_pnl = float(
            monte_carlo.get(
                "worst_final_pnl",
                0.0,
            )
        )

        worst_drawdown = float(
            monte_carlo.get(
                "worst_max_drawdown",
                0.0,
            )
        )

        stress_survival = 0.0

        if stress_tests:

            surviving = sum(
                1
                for result in stress_tests
                if float(
                    result.get(
                        "total_pnl",
                        0.0,
                    )
                ) >= 0
            )

            stress_survival = (
                surviving
                / len(stress_tests)
            )

        # -----------------------------------------------------
        # Normalize components
        # -----------------------------------------------------

        probability_score = (
            probability * 40.0
        )

        stress_score = (
            stress_survival * 30.0
        )

        worst_case_score = (
            20.0
            if worst_pnl >= 0
            else 0.0
        )

        drawdown_score = (
            10.0
            if worst_drawdown
            <= MAX_ACCEPTABLE_DRAWDOWN
            else 0.0
        )

        score = (
            probability_score
            + stress_score
            + worst_case_score
            + drawdown_score
        )

        return round(
            score,
            6,
        )

    # ---------------------------------------------------------
    # ANALYZE
    # ---------------------------------------------------------

    def analyze(
        self,
        monte_carlo: Dict,
        stress_tests: List[Dict],
    ) -> Dict:

        score = self.calculate_score(
            monte_carlo=monte_carlo,
            stress_tests=stress_tests,
        )

        probability = float(
            monte_carlo.get(
                "probability_of_profit",
                0.0,
            )
        )

        worst_pnl = float(
            monte_carlo.get(
                "worst_final_pnl",
                0.0,
            )
        )

        stress_failures = sum(
            1
            for result in stress_tests
            if float(
                result.get(
                    "total_pnl",
                    0.0,
                )
            ) < 0
        )

        robust = (
            score >= MIN_ROBUSTNESS_SCORE
            and probability
            >= MIN_PROFIT_PROBABILITY
            and worst_pnl >= 0
        )

        return {
            "robustness_score": score,
            "minimum_required_score": (
                MIN_ROBUSTNESS_SCORE
            ),
            "probability_of_profit": (
                probability
            ),
            "minimum_required_profit_probability": (
                MIN_PROFIT_PROBABILITY
            ),
            "worst_case_pnl": (
                worst_pnl
            ),
            "stress_failures": (
                stress_failures
            ),
            "robust": bool(
                robust
            ),
        }
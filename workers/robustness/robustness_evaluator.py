from typing import Dict

from config.phase18_config import (
    MIN_POSITIVE_SCENARIO_RATE,
    ROBUSTNESS_THRESHOLD,
)


class Phase18RobustnessEvaluator:

    # --------------------------------------------------------
    # EVALUATE MONTE CARLO
    # --------------------------------------------------------

    def evaluate_monte_carlo(
        self,
        result: Dict,
    ) -> Dict:

        positive_rate = float(
            result.get(
                "positive_scenario_rate",
                0.0,
            )
        )

        worst_pnl = float(
            result.get(
                "worst_pnl",
                0.0,
            )
        )

        robust = (
            positive_rate
            >= MIN_POSITIVE_SCENARIO_RATE
        )

        return {
            "positive_scenario_rate": round(
                positive_rate,
                6,
            ),
            "worst_pnl": round(
                worst_pnl,
                6,
            ),
            "robust": bool(
                robust
            ),
        }

    # --------------------------------------------------------
    # EVALUATE STRESS
    # --------------------------------------------------------

    def evaluate_stress(
        self,
        result: Dict,
    ) -> Dict:

        positive_rate = float(
            result.get(
                "positive_scenario_rate",
                0.0,
            )
        )

        robust = (
            positive_rate
            >= MIN_POSITIVE_SCENARIO_RATE
        )

        return {
            "positive_scenario_rate": round(
                positive_rate,
                6,
            ),
            "robust": bool(
                robust
            ),
        }

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    def final_score(
        self,
        monte_carlo: Dict,
        stress: Dict,
    ) -> float:

        mc_rate = float(
            monte_carlo.get(
                "positive_scenario_rate",
                0.0,
            )
        )

        stress_rate = float(
            stress.get(
                "positive_scenario_rate",
                0.0,
            )
        )

        score = (
            mc_rate * 0.50
            + stress_rate * 0.50
        )

        return round(
            score,
            6,
        )

    # --------------------------------------------------------
    # COMPLETE EVALUATION
    # --------------------------------------------------------

    def evaluate(
        self,
        monte_carlo: Dict,
        stress: Dict,
    ) -> Dict:

        mc = self.evaluate_monte_carlo(
            monte_carlo
        )

        stress_result = self.evaluate_stress(
            stress
        )

        score = self.final_score(
            monte_carlo,
            stress,
        )

        robust = (
            score
            >= ROBUSTNESS_THRESHOLD
        )

        return {
            "monte_carlo": mc,
            "stress_testing": stress_result,
            "robustness_score": score,
            "robust": bool(
                robust
            ),
        }

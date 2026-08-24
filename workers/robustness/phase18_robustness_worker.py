import json
from pathlib import Path
from typing import Dict, List, Optional

from config.phase18_config import (
    MONTE_CARLO_RUNS,
    RANDOM_SEED,
    REPORT_DIRECTORY,
    REPORT_FILENAME,
    STRESS_MULTIPLIERS,
    DEFAULT_SYMBOL,
)

from workers.robustness.monte_carlo import (
    MonteCarloSimulator,
)

from workers.robustness.stress_test import (
    StressTester,
)

from workers.robustness.robustness_analyzer import (
    RobustnessAnalyzer,
)


class Phase18RobustnessWorker:

    def __init__(
        self,
        monte_carlo_runs: int = MONTE_CARLO_RUNS,
        random_seed: int = RANDOM_SEED,
    ):

        self.monte_carlo = (
            MonteCarloSimulator(
                runs=monte_carlo_runs,
                seed=random_seed,
            )
        )

        self.stress = (
            StressTester()
        )

        self.analyzer = (
            RobustnessAnalyzer()
        )

    # ---------------------------------------------------------
    # EXTRACT OOS P&L
    # ---------------------------------------------------------

    def extract_oos_pnl(
        self,
        walk_forward_result: Dict,
    ) -> List[float]:

        cycles = walk_forward_result.get(
            "cycles",
            [],
        )

        pnl_values = []

        for cycle in cycles:

            testing_metrics = cycle.get(
                "testing_metrics",
                {},
            )

            pnl = float(
                testing_metrics.get(
                    "realized_pnl",
                    0.0,
                )
            )

            pnl_values.append(
                pnl
            )

        if not pnl_values:

            summary = (
                walk_forward_result.get(
                    "summary",
                    {},
                )
            )

            total_oos = float(
                summary.get(
                    "total_out_of_sample_pnl",
                    0.0,
                )
            )

            if total_oos != 0.0:
                pnl_values = [
                    total_oos
                ]

        return pnl_values

    # ---------------------------------------------------------
    # VALIDATE INPUT
    # ---------------------------------------------------------

    def validate_input(
        self,
        walk_forward_result: Dict,
    ):

        if not isinstance(
            walk_forward_result,
            dict,
        ):
            raise ValueError(
                "Phase 18 requires a "
                "walk-forward result dictionary."
            )

        cycles = (
            walk_forward_result.get(
                "cycles",
                [],
            )
        )

        if not cycles:
            raise ValueError(
                "Phase 18 requires at least "
                "one walk-forward cycle."
            )

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------

    def run(
        self,
        walk_forward_result: Dict,
        symbol: str = DEFAULT_SYMBOL,
    ) -> Dict:

        self.validate_input(
            walk_forward_result
        )

        pnl_values = (
            self.extract_oos_pnl(
                walk_forward_result
            )
        )

        if not pnl_values:
            raise ValueError(
                "No out-of-sample P&L "
                "available for robustness analysis."
            )

        monte_carlo = (
            self.monte_carlo.run(
                pnl_values=pnl_values
            )
        )

        stress_tests = (
            self.stress.run(
                pnl_values=pnl_values,
                multipliers=(
                    STRESS_MULTIPLIERS
                ),
            )
        )

        robustness = (
            self.analyzer.analyze(
                monte_carlo=monte_carlo,
                stress_tests=stress_tests,
            )
        )

        summary = (
            walk_forward_result.get(
                "summary",
                {},
            )
        )

        return {
            "phase": 18,
            "symbol": symbol,
            "input": {
                "walk_forward_cycles": len(
                    walk_forward_result.get(
                        "cycles",
                        [],
                    )
                ),
                "oos_pnl_values": pnl_values,
                "total_oos_pnl": float(
                    summary.get(
                        "total_out_of_sample_pnl",
                        sum(pnl_values),
                    )
                ),
            },
            "monte_carlo": monte_carlo,
            "stress_tests": stress_tests,
            "robustness": robustness,
        }

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    def save_report(
        self,
        result: Dict,
        filename: str = REPORT_FILENAME,
    ) -> str:

        directory = Path(
            REPORT_DIRECTORY
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            / filename
        )

        path.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(path)
import random
from typing import Dict, Iterable, List, Optional

from config.phase18_config import (
    MONTE_CARLO_ITERATIONS,
    RANDOM_SEED,
)


class Phase18MonteCarlo:

    def __init__(
        self,
        iterations: int = MONTE_CARLO_ITERATIONS,
        seed: int = RANDOM_SEED,
    ):

        if iterations <= 0:
            raise ValueError(
                "Monte Carlo iterations must be positive."
            )

        self.iterations = int(iterations)
        self.seed = int(seed)

    # --------------------------------------------------------
    # EXTRACT PNL
    # --------------------------------------------------------

    def extract_pnls(
        self,
        trades: Optional[Iterable[Dict]],
    ) -> List[float]:

        pnls = []

        if not trades:
            return pnls

        for trade in trades:

            if not isinstance(trade, dict):
                continue

            value = None

            for key in (
                "realized_pnl",
                "pnl",
                "profit",
                "profit_loss",
            ):

                if key in trade:
                    value = trade[key]
                    break

            if value is None:
                continue

            try:
                pnls.append(float(value))
            except (
                TypeError,
                ValueError,
            ):
                continue

        return pnls

    # --------------------------------------------------------
    # ONE SIMULATION
    # --------------------------------------------------------

    def simulate_once(
        self,
        pnls: List[float],
        rng: random.Random,
    ) -> Dict:

        if not pnls:
            return {
                "total_pnl": 0.0,
                "max_drawdown": 0.0,
                "ending_equity_change": 0.0,
                "win_rate": 0.0,
            }

        shuffled = list(pnls)

        rng.shuffle(shuffled)

        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0

        wins = 0

        for pnl in shuffled:

            equity += pnl

            if pnl > 0:
                wins += 1

            if equity > peak:
                peak = equity

            drawdown = peak - equity

            if drawdown > max_drawdown:
                max_drawdown = drawdown

        win_rate = (
            wins / len(shuffled)
            if shuffled
            else 0.0
        )

        return {
            "total_pnl": round(
                equity,
                6,
            ),
            "max_drawdown": round(
                max_drawdown,
                6,
            ),
            "ending_equity_change": round(
                equity,
                6,
            ),
            "win_rate": round(
                win_rate,
                6,
            ),
        }

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(
        self,
        trades: Optional[Iterable[Dict]],
    ) -> Dict:

        pnls = self.extract_pnls(
            trades
        )

        rng = random.Random(
            self.seed
        )

        simulations = []

        positive = 0

        total_pnl = 0.0

        worst_pnl = None
        best_pnl = None

        for iteration in range(
            1,
            self.iterations + 1,
        ):

            result = self.simulate_once(
                pnls,
                rng,
            )

            result["iteration"] = iteration

            simulations.append(result)

            pnl = result["total_pnl"]

            total_pnl += pnl

            if pnl > 0:
                positive += 1

            if (
                worst_pnl is None
                or pnl < worst_pnl
            ):
                worst_pnl = pnl

            if (
                best_pnl is None
                or pnl > best_pnl
            ):
                best_pnl = pnl

        average_pnl = (
            total_pnl / self.iterations
            if self.iterations
            else 0.0
        )

        positive_rate = (
            positive / self.iterations
            if self.iterations
            else 0.0
        )

        return {
            "trade_count": len(pnls),
            "iterations": self.iterations,
            "seed": self.seed,
            "average_pnl": round(
                average_pnl,
                6,
            ),
            "best_pnl": round(
                best_pnl or 0.0,
                6,
            ),
            "worst_pnl": round(
                worst_pnl or 0.0,
                6,
            ),
            "positive_scenario_rate": round(
                positive_rate,
                6,
            ),
            "simulations": simulations,
        }

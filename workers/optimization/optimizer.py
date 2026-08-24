import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from config.phase16_config import (
    INITIAL_CAPITAL,
    REPORT_DIRECTORY,
    REPORT_FILENAME,
)

from workers.backtest.phase15_backtest_worker import (
    Phase15BacktestWorker,
)

from workers.optimization.evaluation import (
    Phase16Evaluator,
)

from workers.optimization.parameter_space import (
    Phase16ParameterSpace,
)


class Phase16Optimizer:

    def __init__(
        self,
        intelligence_worker_factory,
        initial_capital: float = INITIAL_CAPITAL,
        parameter_space: Optional[
            Phase16ParameterSpace
        ] = None,
    ):

        self.intelligence_worker_factory = (
            intelligence_worker_factory
        )

        self.initial_capital = float(
            initial_capital
        )

        self.parameter_space = (
            parameter_space
            or Phase16ParameterSpace()
        )

        self.evaluator = (
            Phase16Evaluator()
        )

        self.evaluations: List[Dict] = []

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self):

        self.evaluations = []

    # ---------------------------------------------------------
    # RUN ONE CONFIGURATION
    # ---------------------------------------------------------

    def run_configuration(
        self,
        candles: List[Dict],
        configuration: Dict,
        symbol: str,
        news: Optional[
            Iterable[Dict | str]
        ],
        final_exit_price: Optional[float],
    ) -> Dict:

        quantity = int(
            configuration["quantity"]
        )

        confidence = float(
            configuration[
                "min_ai_confidence"
            ]
        )

        intelligence_worker = (
            self.intelligence_worker_factory(
                min_ai_confidence=confidence
            )
        )

        backtest = Phase15BacktestWorker(
            intelligence_worker=(
                intelligence_worker
            ),
            initial_capital=(
                self.initial_capital
            ),
        )

        result = backtest.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            news=news,
            final_exit_price=(
                final_exit_price
            ),
        )

        evaluation = self.evaluator.evaluate(
            configuration=configuration,
            result=result,
        )

        return evaluation

    # ---------------------------------------------------------
    # OPTIMIZE
    # ---------------------------------------------------------

    def run(
        self,
        candles: List[Dict],
        symbol: str = "NIFTY",
        news: Optional[
            Iterable[Dict | str]
        ] = None,
        final_exit_price: Optional[float] = None,
    ) -> Dict:

        if not candles:
            raise ValueError(
                "Optimization requires historical candles."
            )

        self.reset()

        configurations = (
            self.parameter_space.generate()
        )

        for configuration in configurations:

            evaluation = (
                self.run_configuration(
                    candles=candles,
                    configuration=configuration,
                    symbol=symbol,
                    news=news,
                    final_exit_price=(
                        final_exit_price
                    ),
                )
            )

            self.evaluations.append(
                evaluation
            )

        ranked = self.evaluator.rank(
            self.evaluations
        )

        best = (
            ranked[0]
            if ranked
            else None
        )

        return {
            "symbol": symbol,
            "candles": len(candles),
            "configurations_tested": len(
                configurations
            ),
            "results": ranked,
            "best_configuration": (
                best["configuration"]
                if best
                else None
            ),
            "best_metrics": (
                best["metrics"]
                if best
                else None
            ),
            "best_score": (
                best["ranking_score"]
                if best
                else None
            ),
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

        path = directory / filename

        path.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        return str(path)

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from config.phase17_config import (
    DEFAULT_QUANTITY,
    DEFAULT_SYMBOL,
    MIN_TEST_SIZE,
    MIN_TRAINING_SIZE,
    OVERFITTING_THRESHOLD,
    REPORT_DIRECTORY,
    STEP_SIZE,
    TEST_SIZE,
    TRAINING_SIZE,
)

from workers.backtest.phase15_backtest_worker import (
    Phase15BacktestWorker,
)

from workers.optimization.optimizer import (
    Phase16Optimizer,
)

from workers.validation.walk_forward_splitter import (
    WalkForwardSplitter,
)


class WalkForwardValidator:

    def __init__(
        self,
        intelligence_worker_factory,
        initial_capital: float = 100000.0,
    ):

        self.intelligence_worker_factory = (
            intelligence_worker_factory
        )

        self.initial_capital = float(
            initial_capital
        )

        self.splitter = WalkForwardSplitter(
            training_size=TRAINING_SIZE,
            test_size=TEST_SIZE,
            step_size=STEP_SIZE,
        )

    # ---------------------------------------------------------
    # TRAINING / OPTIMIZATION
    # ---------------------------------------------------------

    def optimize_training_window(
        self,
        candles: List[Dict],
        symbol: str,
        news: Optional[
            Iterable[Dict | str]
        ],
        final_exit_price: Optional[float],
    ):

        optimizer = Phase16Optimizer(
            intelligence_worker_factory=(
                self.intelligence_worker_factory
            ),
            initial_capital=(
                self.initial_capital
            ),
        )

        return optimizer.run(
            candles=candles,
            symbol=symbol,
            news=news,
            final_exit_price=(
                final_exit_price
            ),
        )

    # ---------------------------------------------------------
    # OUT-OF-SAMPLE TEST
    # ---------------------------------------------------------

    def backtest_test_window(
        self,
        candles: List[Dict],
        symbol: str,
        quantity: int,
        confidence: float,
        news: Optional[
            Iterable[Dict | str]
        ],
        final_exit_price: Optional[float],
    ):

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

        return backtest.run(
            candles=candles,
            symbol=symbol,
            quantity=quantity,
            news=news,
            final_exit_price=(
                final_exit_price
            ),
        )

    # ---------------------------------------------------------
    # GENERALIZATION
    # ---------------------------------------------------------

    def calculate_generalization(
        self,
        training_pnl: float,
        testing_pnl: float,
    ) -> Dict:

        training_pnl = float(
            training_pnl
        )

        testing_pnl = float(
            testing_pnl
        )

        if training_pnl > 0:

            ratio = (
                testing_pnl
                / training_pnl
            )

        elif training_pnl == 0:

            ratio = (
                1.0
                if testing_pnl >= 0
                else 0.0
            )

        else:

            ratio = (
                testing_pnl
                / abs(training_pnl)
            )

        overfitting = (
            ratio < OVERFITTING_THRESHOLD
        )

        return {
            "generalization_ratio": round(
                ratio,
                6,
            ),
            "overfitting_detected": bool(
                overfitting
            ),
        }

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------

    def run(
        self,
        candles: List[Dict],
        symbol: str = DEFAULT_SYMBOL,
        quantity: int = DEFAULT_QUANTITY,
        news: Optional[
            Iterable[Dict | str]
        ] = None,
    ):

        if not candles:
            raise ValueError(
                "Walk-forward validation "
                "requires historical candles."
            )

        if len(candles) < (
            MIN_TRAINING_SIZE
            + MIN_TEST_SIZE
        ):
            raise ValueError(
                "Not enough candles for "
                "walk-forward validation."
            )

        windows = self.splitter.split(
            candles
        )

        if not windows:
            raise ValueError(
                "No valid walk-forward windows."
            )

        cycles = []

        total_training_pnl = 0.0
        total_testing_pnl = 0.0

        for window in windows:

            training = window[
                "training"
            ]

            testing = window[
                "testing"
            ]

            training_exit_price = float(
                training[-1]["close"]
            )

            optimization = (
                self.optimize_training_window(
                    candles=training,
                    symbol=symbol,
                    news=news,
                    final_exit_price=(
                        training_exit_price
                    ),
                )
            )

            best_configuration = (
                optimization[
                    "best_configuration"
                ]
            )

            best_metrics = (
                optimization[
                    "best_metrics"
                ]
            )

            if best_configuration is None:
                raise RuntimeError(
                    "Phase 16 optimizer returned "
                    "no best configuration."
                )

            if best_metrics is None:
                raise RuntimeError(
                    "Phase 16 optimizer returned "
                    "no best metrics."
                )

            best_quantity = int(
                best_configuration.get(
                    "quantity",
                    quantity,
                )
            )

            best_confidence = float(
                best_configuration.get(
                    "min_ai_confidence",
                    0.0,
                )
            )

            testing_exit_price = float(
                testing[-1]["close"]
            )

            testing_result = (
                self.backtest_test_window(
                    candles=testing,
                    symbol=symbol,
                    quantity=best_quantity,
                    confidence=best_confidence,
                    news=news,
                    final_exit_price=(
                        testing_exit_price
                    ),
                )
            )

            testing_metrics = (
                testing_result["metrics"]
            )

            training_pnl = float(
                best_metrics.get(
                    "realized_pnl",
                    0.0,
                )
            )

            testing_pnl = float(
                testing_metrics.get(
                    "realized_pnl",
                    0.0,
                )
            )

            generalization = (
                self.calculate_generalization(
                    training_pnl=training_pnl,
                    testing_pnl=testing_pnl,
                )
            )

            total_training_pnl += (
                training_pnl
            )

            total_testing_pnl += (
                testing_pnl
            )

            cycles.append(
                {
                    "cycle": window[
                        "cycle"
                    ],
                    "training_range": {
                        "start": window[
                            "training_start"
                        ],
                        "end": window[
                            "training_end"
                        ],
                        "candles": len(
                            training
                        ),
                    },
                    "testing_range": {
                        "start": window[
                            "test_start"
                        ],
                        "end": window[
                            "test_end"
                        ],
                        "candles": len(
                            testing
                        ),
                    },
                    "best_configuration": (
                        best_configuration
                    ),
                    "training_metrics": (
                        best_metrics
                    ),
                    "testing_metrics": (
                        testing_metrics
                    ),
                    "generalization": (
                        generalization
                    ),
                }
            )

        cycle_count = len(
            cycles
        )

        average_testing_pnl = (
            total_testing_pnl
            / cycle_count
            if cycle_count
            else 0.0
        )

        overfitting_cycles = sum(
            1
            for cycle in cycles
            if cycle[
                "generalization"
            ][
                "overfitting_detected"
            ]
        )

        return {
            "symbol": symbol,
            "candles": len(candles),
            "training_size": TRAINING_SIZE,
            "test_size": TEST_SIZE,
            "step_size": STEP_SIZE,
            "cycles": cycles,
            "summary": {
                "cycles": cycle_count,
                "total_training_pnl": round(
                    total_training_pnl,
                    6,
                ),
                "total_out_of_sample_pnl": round(
                    total_testing_pnl,
                    6,
                ),
                "average_out_of_sample_pnl": round(
                    average_testing_pnl,
                    6,
                ),
                "overfitting_cycles": (
                    overfitting_cycles
                ),
                "overfitting_detected": (
                    overfitting_cycles > 0
                ),
            },
        }

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    def save_report(
        self,
        result: Dict,
        filename: str = (
            "phase17_walk_forward_report.json"
        ),
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

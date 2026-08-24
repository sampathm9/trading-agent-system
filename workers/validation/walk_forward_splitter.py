from typing import Dict, List


class WalkForwardSplitter:

    def __init__(
        self,
        training_size: int,
        test_size: int,
        step_size: int,
    ):

        if training_size <= 0:
            raise ValueError(
                "training_size must be positive"
            )

        if test_size <= 0:
            raise ValueError(
                "test_size must be positive"
            )

        if step_size <= 0:
            raise ValueError(
                "step_size must be positive"
            )

        self.training_size = training_size
        self.test_size = test_size
        self.step_size = step_size

    def split(
        self,
        candles: List[Dict],
    ):

        if not candles:
            raise ValueError(
                "candles cannot be empty"
            )

        windows = []

        start = 0

        while True:

            train_start = start
            train_end = (
                train_start
                + self.training_size
            )

            test_start = train_end
            test_end = (
                test_start
                + self.test_size
            )

            if test_end > len(candles):
                break

            training = candles[
                train_start:train_end
            ]

            testing = candles[
                test_start:test_end
            ]

            windows.append(
                {
                    "cycle": len(windows) + 1,
                    "training_start": train_start,
                    "training_end": train_end,
                    "test_start": test_start,
                    "test_end": test_end,
                    "training": training,
                    "testing": testing,
                }
            )

            start += self.step_size

        return windows

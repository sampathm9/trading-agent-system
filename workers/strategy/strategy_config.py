class StrategyConfig:

    def __init__(
        self,
        short_period=5,
        long_period=10,
        momentum_period=5,
        minimum_confidence=0.60,
    ):

        self.short_period = int(
            short_period
        )

        self.long_period = int(
            long_period
        )

        self.momentum_period = int(
            momentum_period
        )

        self.minimum_confidence = float(
            minimum_confidence
        )

        if self.short_period <= 0:
            raise ValueError(
                "short_period must be greater than zero"
            )

        if self.long_period <= self.short_period:
            raise ValueError(
                "long_period must be greater than short_period"
            )

        if self.momentum_period <= 0:
            raise ValueError(
                "momentum_period must be greater than zero"
            )

        if not 0.0 <= self.minimum_confidence <= 1.0:
            raise ValueError(
                "minimum_confidence must be between 0 and 1"
            )

    def to_dict(self):

        return {
            "short_period": self.short_period,
            "long_period": self.long_period,
            "momentum_period": self.momentum_period,
            "minimum_confidence": self.minimum_confidence,
        }
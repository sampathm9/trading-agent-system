from itertools import product
from typing import Dict, List

from config.phase16_config import (
    QUANTITY_VALUES,
    MIN_AI_CONFIDENCE_VALUES,
)


class Phase16ParameterSpace:

    def __init__(
        self,
        quantities: List[int] = None,
        confidence_values: List[float] = None,
    ):

        self.quantities = (
            list(quantities)
            if quantities is not None
            else list(QUANTITY_VALUES)
        )

        self.confidence_values = (
            list(confidence_values)
            if confidence_values is not None
            else list(MIN_AI_CONFIDENCE_VALUES)
        )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    def validate(self):

        if not self.quantities:
            raise ValueError(
                "Quantity parameter space cannot be empty."
            )

        if not self.confidence_values:
            raise ValueError(
                "Confidence parameter space cannot be empty."
            )

        for quantity in self.quantities:

            if not isinstance(
                quantity,
                int,
            ):
                raise ValueError(
                    "Quantity must be an integer."
                )

            if quantity <= 0:
                raise ValueError(
                    "Quantity must be positive."
                )

        for confidence in self.confidence_values:

            if not 0.0 <= float(confidence) <= 1.0:
                raise ValueError(
                    "AI confidence must be between 0 and 1."
                )

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    def generate(self) -> List[Dict]:

        self.validate()

        configurations = []

        for quantity, confidence in product(
            self.quantities,
            self.confidence_values,
        ):

            configurations.append(
                {
                    "quantity": int(quantity),
                    "min_ai_confidence": float(
                        confidence
                    ),
                }
            )

        return configurations

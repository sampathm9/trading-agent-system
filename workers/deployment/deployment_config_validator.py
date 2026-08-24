from typing import Dict

from config.phase22_config import (
    PAPER_MODE,
    LIVE_TRADING_ENABLED,
    REAL_BROKER_ENABLED,
    MAX_ORDER_QUANTITY,
    MAX_DAILY_TRADES,
    MAX_DAILY_LOSS,
    ENVIRONMENT,
    ALLOWED_ENVIRONMENTS,
)


class DeploymentConfigValidator:

    def validate(self) -> Dict:

        errors = []

        if ENVIRONMENT not in ALLOWED_ENVIRONMENTS:
            errors.append(
                f"Invalid environment: {ENVIRONMENT}"
            )

        if MAX_ORDER_QUANTITY <= 0:
            errors.append(
                "MAX_ORDER_QUANTITY must be greater than zero"
            )

        if MAX_DAILY_TRADES <= 0:
            errors.append(
                "MAX_DAILY_TRADES must be greater than zero"
            )

        if MAX_DAILY_LOSS <= 0:
            errors.append(
                "MAX_DAILY_LOSS must be greater than zero"
            )

        if ENVIRONMENT == "PAPER":

            if not PAPER_MODE:
                errors.append(
                    "Paper environment requires PAPER_MODE=True"
                )

            if LIVE_TRADING_ENABLED:
                errors.append(
                    "Live trading must be disabled in paper mode"
                )

            if REAL_BROKER_ENABLED:
                errors.append(
                    "Real broker must be disabled in paper mode"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "environment": ENVIRONMENT,
            "paper_mode": PAPER_MODE,
            "live_trading_enabled": LIVE_TRADING_ENABLED,
            "real_broker_enabled": REAL_BROKER_ENABLED,
        }

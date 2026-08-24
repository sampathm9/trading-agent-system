from typing import Dict


class Phase19SafetyGate:

    def __init__(
        self,
        max_trades: int,
        max_daily_loss: float,
        max_consecutive_losses: int,
        paper_only: bool = True,
        allow_real_broker: bool = False,
    ):

        self.max_trades = int(max_trades)
        self.max_daily_loss = float(max_daily_loss)
        self.max_consecutive_losses = int(
            max_consecutive_losses
        )

        self.paper_only = bool(paper_only)
        self.allow_real_broker = bool(
            allow_real_broker
        )

    # ---------------------------------------------------------
    # BROKER SAFETY
    # ---------------------------------------------------------

    def validate_broker(
        self,
        broker,
    ) -> Dict:

        broker_name = type(broker).__name__

        is_paper = (
            broker_name == "PaperBroker"
        )

        if self.paper_only and not is_paper:

            return {
                "allowed": False,
                "reason": (
                    "Phase 19 requires PaperBroker."
                ),
                "broker": broker_name,
            }

        if not self.allow_real_broker and not is_paper:

            return {
                "allowed": False,
                "reason": (
                    "Real broker execution is disabled."
                ),
                "broker": broker_name,
            }

        return {
            "allowed": True,
            "reason": "Paper broker accepted.",
            "broker": broker_name,
        }

    # ---------------------------------------------------------
    # TRADE LIMIT
    # ---------------------------------------------------------

    def can_trade(
        self,
        total_trades: int,
        realized_pnl: float,
        consecutive_losses: int,
    ) -> Dict:

        if total_trades >= self.max_trades:

            return {
                "allowed": False,
                "reason": "Maximum trade count reached.",
            }

        if realized_pnl <= -abs(
            self.max_daily_loss
        ):

            return {
                "allowed": False,
                "reason": "Maximum daily loss reached.",
            }

        if consecutive_losses >= (
            self.max_consecutive_losses
        ):

            return {
                "allowed": False,
                "reason": (
                    "Maximum consecutive losses reached."
                ),
            }

        return {
            "allowed": True,
            "reason": "Trading permitted.",
        }

    # ---------------------------------------------------------
    # FINAL SAFETY
    # ---------------------------------------------------------

    def final_check(
        self,
        broker,
    ) -> Dict:

        broker_check = self.validate_broker(
            broker
        )

        if not broker_check["allowed"]:

            return broker_check

        return {
            "allowed": True,
            "reason": (
                "Phase 19 safety checks passed."
            ),
        }

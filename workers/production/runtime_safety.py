from typing import Dict


class Phase20RuntimeSafety:

    def __init__(
        self,
        max_quantity: int,
        max_trades: int,
        max_loss: float,
        allow_live_trading: bool = False,
        allow_real_orders: bool = False,
    ):

        self.max_quantity = int(
            max_quantity
        )

        self.max_trades = int(
            max_trades
        )

        self.max_loss = float(
            max_loss
        )

        self.allow_live_trading = bool(
            allow_live_trading
        )

        self.allow_real_orders = bool(
            allow_real_orders
        )

    def check_mode(
        self,
        mode: str,
    ) -> Dict:

        mode = str(mode).upper()

        if mode != "PAPER":
            return {
                "allowed": False,
                "reason": (
                    "Phase 20 permits PAPER mode only."
                ),
            }

        return {
            "allowed": True,
            "reason": "Paper mode allowed.",
        }

    def check_order(
        self,
        quantity: int,
        trade_count: int,
        realized_pnl: float,
        mode: str,
    ) -> Dict:

        mode_result = self.check_mode(
            mode
        )

        if not mode_result["allowed"]:
            return mode_result

        if quantity <= 0:
            return {
                "allowed": False,
                "reason": "Quantity must be positive.",
            }

        if quantity > self.max_quantity:
            return {
                "allowed": False,
                "reason": "Quantity exceeds Phase 20 limit.",
            }

        if trade_count >= self.max_trades:
            return {
                "allowed": False,
                "reason": "Maximum session trades reached.",
            }

        if realized_pnl <= -self.max_loss:
            return {
                "allowed": False,
                "reason": "Maximum session loss reached.",
            }

        if self.allow_live_trading:
            return {
                "allowed": False,
                "reason": (
                    "Live trading must remain disabled "
                    "during Phase 20."
                ),
            }

        if self.allow_real_orders:
            return {
                "allowed": False,
                "reason": (
                    "Real broker orders must remain disabled "
                    "during Phase 20."
                ),
            }

        return {
            "allowed": True,
            "reason": "Order passed Phase 20 safety checks.",
        }

    def can_trade(
        self,
        quantity: int,
        trade_count: int,
        realized_pnl: float,
        mode: str = "PAPER",
    ) -> Dict:

        return self.check_order(
            quantity=quantity,
            trade_count=trade_count,
            realized_pnl=realized_pnl,
            mode=mode,
        )

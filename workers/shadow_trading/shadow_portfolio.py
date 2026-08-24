from typing import Dict, List, Optional


class ShadowPortfolio:

    def __init__(
        self,
        initial_capital: float = 100000.0,
    ):
        self.initial_capital = float(initial_capital)

        self.cash = float(initial_capital)

        self.position_quantity = 0
        self.position_symbol: Optional[str] = None
        self.entry_price: Optional[float] = None
        self.entry_value: float = 0.0

        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

        self.trades: List[Dict] = []

        self.winning_trades = 0
        self.losing_trades = 0
        self.consecutive_losses = 0
        self.max_consecutive_losses = 0

    # ---------------------------------------------------------
    # ENTER
    # ---------------------------------------------------------

    def enter(
        self,
        symbol: str,
        quantity: int,
        price: float,
        timestamp=None,
        reason: str = "",
    ) -> Dict:

        quantity = int(quantity)
        price = float(price)

        if quantity <= 0:
            raise ValueError("Shadow quantity must be positive.")

        if self.position_quantity != 0:
            raise RuntimeError(
                "Shadow portfolio already has an open position."
            )

        value = quantity * price

        self.position_quantity = quantity
        self.position_symbol = symbol
        self.entry_price = price
        self.entry_value = value

        return {
            "action": "SHADOW_BUY",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "value": value,
            "timestamp": timestamp,
            "reason": reason,
        }

    # ---------------------------------------------------------
    # EXIT
    # ---------------------------------------------------------

    def exit(
        self,
        price: float,
        timestamp=None,
        reason: str = "",
    ) -> Optional[Dict]:

        if self.position_quantity <= 0:
            return None

        price = float(price)

        quantity = self.position_quantity

        pnl = (
            price - float(self.entry_price)
        ) * quantity

        trade = {
            "action": "SHADOW_SELL",
            "symbol": self.position_symbol,
            "quantity": quantity,
            "entry_price": self.entry_price,
            "exit_price": price,
            "realized_pnl": pnl,
            "timestamp": timestamp,
            "reason": reason,
        }

        self.realized_pnl += pnl

        if pnl > 0:
            self.winning_trades += 1
            self.consecutive_losses = 0
        elif pnl < 0:
            self.losing_trades += 1
            self.consecutive_losses += 1
            self.max_consecutive_losses = max(
                self.max_consecutive_losses,
                self.consecutive_losses,
            )

        self.trades.append(trade)

        self.position_quantity = 0
        self.position_symbol = None
        self.entry_price = None
        self.entry_value = 0.0
        self.unrealized_pnl = 0.0

        return trade

    # ---------------------------------------------------------
    # MARK TO MARKET
    # ---------------------------------------------------------

    def mark_to_market(
        self,
        price: float,
    ) -> float:

        price = float(price)

        if (
            self.position_quantity > 0
            and self.entry_price is not None
        ):
            self.unrealized_pnl = (
                price - self.entry_price
            ) * self.position_quantity
        else:
            self.unrealized_pnl = 0.0

        return self.unrealized_pnl

    # ---------------------------------------------------------
    # CLOSE
    # ---------------------------------------------------------

    def close(
        self,
        final_price: float,
        timestamp=None,
    ):

        return self.exit(
            price=final_price,
            timestamp=timestamp,
            reason="PHASE23_SESSION_CLOSE",
        )

    # ---------------------------------------------------------
    # SNAPSHOT
    # ---------------------------------------------------------

    def snapshot(self) -> Dict:

        total_pnl = (
            self.realized_pnl
            + self.unrealized_pnl
        )

        return {
            "initial_capital": self.initial_capital,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "total_pnl": total_pnl,
            "position_quantity": self.position_quantity,
            "position_symbol": self.position_symbol,
            "entry_price": self.entry_price,
            "trades": len(self.trades),
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "consecutive_losses": self.consecutive_losses,
            "max_consecutive_losses": self.max_consecutive_losses,
        }

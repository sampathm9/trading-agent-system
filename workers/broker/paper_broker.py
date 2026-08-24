from typing import List
from uuid import uuid4

from workers.broker.broker_interface import BrokerInterface
from workers.broker.models import (
    OrderRequest,
    OrderResult,
    OrderSide,
    OrderStatus,
)


class PaperBroker(BrokerInterface):

    def __init__(self):
        self._positions = {}
        self.orders = {}

    # ---------------------------------------------------------
    # CONNECTION
    # ---------------------------------------------------------

    def is_connected(self) -> bool:
        return True

    # ---------------------------------------------------------
    # PLACE ORDER
    # ---------------------------------------------------------

    def place_order(
        self,
        order: OrderRequest,
    ) -> OrderResult:

        if order.quantity <= 0:

            result = OrderResult(
                order_id=str(uuid4()),
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=order.price,
                status=OrderStatus.REJECTED,
                message="Quantity must be greater than zero",
            )

            self.orders[result.order_id] = result

            return result

        if order.price is None:

            result = OrderResult(
                order_id=str(uuid4()),
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=None,
                status=OrderStatus.REJECTED,
                message=(
                    "Paper broker requires an execution price"
                ),
            )

            self.orders[result.order_id] = result

            return result

        current = self._positions.get(
            order.symbol,
            {
                "quantity": 0,
                "average_price": 0.0,
            },
        )

        quantity = current["quantity"]
        average_price = current["average_price"]

        realized_pnl = None

        # -----------------------------------------------------
        # BUY
        # -----------------------------------------------------

        if order.side == OrderSide.BUY:

            new_quantity = (
                quantity + order.quantity
            )

            if new_quantity > 0:

                new_average = (
                    (
                        quantity * average_price
                    )
                    + (
                        order.quantity
                        * order.price
                    )
                ) / new_quantity

            else:

                new_average = 0.0

            self._positions[order.symbol] = {
                "quantity": new_quantity,
                "average_price": new_average,
            }

        # -----------------------------------------------------
        # SELL
        # -----------------------------------------------------

        else:

            if order.quantity > quantity:

                result = OrderResult(
                    order_id=str(uuid4()),
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=order.price,
                    status=OrderStatus.REJECTED,
                    message=(
                        "Cannot sell more than paper position"
                    ),
                )

                self.orders[result.order_id] = result

                return result

            realized_pnl = (
                order.price - average_price
            ) * order.quantity

            new_quantity = (
                quantity - order.quantity
            )

            if new_quantity == 0:

                self._positions.pop(
                    order.symbol,
                    None,
                )

            else:

                self._positions[order.symbol] = {
                    "quantity": new_quantity,
                    "average_price": average_price,
                }

        # -----------------------------------------------------
        # ORDER RESULT
        # -----------------------------------------------------

        result = OrderResult(
            order_id=str(uuid4()),
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=order.price,
            status=OrderStatus.FILLED,
            message="Paper order filled",
            realized_pnl=realized_pnl,
        )

        self.orders[result.order_id] = result

        return result

    # ---------------------------------------------------------
    # CLOSE ALL POSITIONS
    # ---------------------------------------------------------

    def close_all_positions(
        self,
        prices: dict[str, float],
    ) -> List[OrderResult]:

        results = []

        for symbol, position in list(
            self._positions.items()
        ):

            quantity = position["quantity"]

            if quantity <= 0:
                continue

            price = prices.get(symbol)

            if price is None:
                continue

            result = self.place_order(
                OrderRequest(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    quantity=quantity,
                    price=price,
                    order_type="MARKET",
                    tag="EOD_EXIT",
                )
            )

            results.append(result)

        return results

    # ---------------------------------------------------------
    # POSITIONS
    # ---------------------------------------------------------

    def positions(self) -> dict:

        return {
            symbol: dict(position)
            for symbol, position
            in self._positions.items()
        }

    # ---------------------------------------------------------
    # GET POSITIONS
    # ---------------------------------------------------------

    def get_positions(self) -> dict:

        return self.positions()

    # ---------------------------------------------------------
    # ORDER STATUS
    # ---------------------------------------------------------

    def get_order_status(
        self,
        order_id: str,
    ) -> OrderResult | None:

        return self.orders.get(order_id)
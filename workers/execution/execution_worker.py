from workers.broker.broker_interface import BrokerInterface
from workers.broker.models import OrderRequest, OrderResult


class ExecutionWorker:

    def __init__(self, broker: BrokerInterface):
        self.broker = broker

    def execute(self, order: OrderRequest) -> OrderResult:

        result = self.broker.place_order(order)

        print(
            "[EXECUTION]",
            result.status.value,
            result.symbol,
            result.side.value,
            result.quantity,
            result.price,
        )

        return result

    def close_all(self, prices: dict[str, float]):

        results = self.broker.close_all_positions(prices)

        for result in results:
            print(
                "[EXECUTION] EOD",
                result.status.value,
                result.symbol,
                result.quantity,
                result.price,
            )

        return results

    def positions(self):
        return self.broker.get_positions()

    def order_status(self, order_id: str):
        return self.broker.get_order_status(order_id)

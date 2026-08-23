from typing import List

from workers.broker.broker_interface import BrokerInterface
from workers.broker.models import OrderRequest, OrderResult


class RealBroker(BrokerInterface):

    def __init__(self):
        self.enabled = False

    def is_connected(self) -> bool:
        return False

    def _disabled(self):
        raise RuntimeError(
            "Real broker execution is disabled in Phase 11. "
            "Complete paper trading validation before enabling broker API execution."
        )

    def place_order(self, order: OrderRequest) -> OrderResult:
        self._disabled()

    def close_all_positions(self, prices: dict[str, float]) -> List[OrderResult]:
        self._disabled()

    def get_positions(self) -> dict:
        self._disabled()

    def get_order_status(self, order_id: str) -> OrderResult | None:
        self._disabled()

from abc import ABC, abstractmethod
from typing import List

from workers.broker.models import OrderRequest, OrderResult


class BrokerInterface(ABC):

    @abstractmethod
    def place_order(self, order: OrderRequest) -> OrderResult:
        raise NotImplementedError

    @abstractmethod
    def close_all_positions(self, prices: dict[str, float]) -> List[OrderResult]:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderResult | None:
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

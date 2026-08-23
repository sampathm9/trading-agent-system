from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


@dataclass
class OrderRequest:
    symbol: str
    side: OrderSide
    quantity: int
    price: Optional[float] = None
    order_type: str = "MARKET"
    tag: str = ""


@dataclass
class OrderResult:
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: Optional[float]
    status: OrderStatus
    message: str = ""
    realized_pnl: Optional[float] = None

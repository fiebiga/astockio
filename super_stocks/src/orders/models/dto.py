from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, condecimal


class OrderType(str, Enum):
    buy = "buy"
    sell = "sell"


class OrderStatus(str, Enum):
    processing = "processing"
    complete = "complete"
    error = "error"


class CreateOrderDto(BaseModel):
    order_type: OrderType
    ticker: str
    user_id: UUID
    amount: condecimal(decimal_places=2, gt=0)


class OrderDto(CreateOrderDto):
    id: UUID
    status: OrderStatus
    created: datetime
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrderDto(BaseModel):
    amount: float
    ticker: str
    user_id: UUID
    id: UUID


class FulfillOrderDto(BaseModel):
    buy: OrderDto
    sell: OrderDto


class FulfilledOrderDto(FulfillOrderDto):
    fulfilled_date: datetime

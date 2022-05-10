from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Order(BaseModel):
    amount: float
    ticker: str
    user_id: UUID
    id: UUID


class FulfilledOrder(BaseModel):
    fulfilled_date: datetime = Field(default_factory=datetime.now)
    buy: Order
    sell: Order
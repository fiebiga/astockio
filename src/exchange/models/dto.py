from uuid import UUID

from pydantic import BaseModel


class ExchangeOrderDto(BaseModel):
    amount: float
    ticker: str
    user_id: UUID
    id: UUID


class ExchangeMatchedOrderDto(BaseModel):
    buy: ExchangeOrderDto
    sell: ExchangeOrderDto
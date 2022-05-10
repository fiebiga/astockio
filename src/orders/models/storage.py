from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from orders.models.dto import OrderType, OrderStatus


class MongoDbBaseModel(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")

    def dict(self, by_alias: bool = True, *args, **kwargs):
        return super().dict(by_alias=by_alias, *args, **kwargs)

    class Config:
        allow_population_by_field_name = True


class Order(MongoDbBaseModel):
    order_type: OrderType
    status: OrderStatus
    ticker: str
    user_id: UUID
    created: datetime = Field(default_factory=datetime.now)
    amount: float
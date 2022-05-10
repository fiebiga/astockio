from pydantic import BaseModel

from exchange.models.dto import ExchangeMatchedOrderDto
from order_fulfillment.models.dto import FulfilledOrderDto, FulfillOrderDto, OrderDto
from order_fulfillment.models.storage import FulfilledOrder, Order


class ExchangeMatchedOrderDtoToFulfillOrderDto(BaseModel):

    @classmethod
    def convert(cls, source: ExchangeMatchedOrderDto) -> FulfillOrderDto:
        return FulfillOrderDto(
            buy=OrderDto(
                amount=source.buy.amount,
                ticker=source.buy.ticker,
                user_id=source.buy.user_id,
                id=source.buy.id
            ),
            sell=OrderDto(
                amount=source.sell.amount,
                ticker=source.sell.ticker,
                user_id=source.sell.user_id,
                id=source.sell.id
            )
        )


class FulfillOrderDtoToFulfilledOrder(BaseModel):

    @classmethod
    def convert(cls, source: FulfillOrderDto) -> FulfilledOrder:
        return FulfilledOrder(
            buy=Order(
                amount=source.buy.amount,
                ticker=source.buy.ticker,
                user_id=source.buy.user_id,
                id=source.buy.id
            ),
            sell=Order(
                amount=source.sell.amount,
                ticker=source.sell.ticker,
                user_id=source.sell.user_id,
                id=source.sell.id
            )
        )


class FulfilledOrderToDtoFulfilledOrderDto(BaseModel):

    @classmethod
    def convert(cls, source: FulfilledOrder) -> FulfilledOrderDto:
        return FulfilledOrderDto(
            fulfilled_date=source.fulfilled_date,
            buy=OrderDto(
                amount=source.buy.amount,
                ticker=source.buy.ticker,
                user_id=source.buy.user_id,
                id=source.buy.id
            ),
            sell=OrderDto(
                amount=source.sell.amount,
                ticker=source.sell.ticker,
                user_id=source.sell.user_id,
                id=source.sell.id
            )
        )

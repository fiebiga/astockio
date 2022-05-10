from exchange.models.dto import ExchangeOrderDto
from orders.models.dto import OrderDto


class OrderDtoToExchangeOrderDto:

    @classmethod
    def convert(cls, source: OrderDto) -> ExchangeOrderDto:
        return ExchangeOrderDto(
            amount=source.amount,
            ticker=source.ticker,
            user_id=source.user_id,
            id=source.id
        )
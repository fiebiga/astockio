from orders.models.dto import CreateOrderDto, OrderDto, OrderStatus
from orders.models.storage import Order


class CreateOrderDtoToOrder:

    @classmethod
    def convert(cls, source: CreateOrderDto) -> Order:
        return Order(
            order_type=source.order_type,
            ticker=source.ticker,
            amount=float(str(source.amount)),
            user_id=source.user_id,
            status=OrderStatus.processing
        )


class OrderToOrderDto:

    @classmethod
    def convert(cls, source: Order) -> OrderDto:
        return OrderDto(
            id=source.id,
            order_type=source.order_type,
            ticker=source.ticker,
            amount=source.amount,
            created=source.created,
            user_id=source.user_id,
            status=source.status
        )

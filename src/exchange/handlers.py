from common.kafka.consumer import KafkaConsumerHandler, kafka_consumer_handler
from common.kafka.model import KafkaEvent
from common.logs import get_logger
from exchange.converter import OrderDtoToExchangeOrderDto
from exchange.service import ExchangeService
from orders.models.dto import OrderDto, OrderType


class OrderCreatedHandler(KafkaConsumerHandler):

    _logger = get_logger(__name__)

    def __init__(self, exchange_service: ExchangeService):
        self._exchange_service = exchange_service

    @kafka_consumer_handler(model=KafkaEvent[OrderDto])
    async def handle_event(self, event: KafkaEvent[OrderDto]):
        self._logger.info(f"[Order ID: {event.data.id}] [User ID: {event.data.user_id}] Received {event.data.order_type.value} order for {event.data.amount}")

        exchange_order = OrderDtoToExchangeOrderDto.convert(event.data)
        if event.data.order_type == OrderType.buy:
            await self._exchange_service.submit_buy_order(exchange_order)
        elif event.data.order_type == OrderType.sell:
            await self._exchange_service.submit_sell_order(exchange_order)

        await self._exchange_service.consume_exchangeable_orders(exchange_order.ticker)


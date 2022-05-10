from common.kafka.consumer import KafkaConsumerHandler, kafka_consumer_handler
from common.kafka.model import KafkaEvent
from common.logs import get_logger
from order_fulfillment.models.dto import FulfilledOrderDto
from orders.models.dto import OrderStatus
from orders.service import OrderService


class OrderFulfilledEventHandler(KafkaConsumerHandler):

    _logger = get_logger(__name__)

    def __init__(self, order_service: OrderService):
        self._order_service = order_service

    @kafka_consumer_handler(model=KafkaEvent[FulfilledOrderDto])
    async def handle_event(self, event: KafkaEvent[FulfilledOrderDto]):
        self._logger.info(f"[Buy Order ID: {event.data.buy.id}] [Sell Order ID: {event.data.sell.id}] Received order fulfilled event")
        await self._order_service.update_order(event.data.buy.id, OrderStatus.complete)
        await self._order_service.update_order(event.data.sell.id, OrderStatus.complete)


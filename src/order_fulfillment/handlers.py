from common.kafka.consumer import KafkaConsumerHandler, kafka_consumer_handler
from common.kafka.model import KafkaEvent
from common.logs import get_logger
from exchange.models.dto import ExchangeMatchedOrderDto
from order_fulfillment.converter import ExchangeMatchedOrderDtoToFulfillOrderDto
from order_fulfillment.error import OrderAlreadyFulfilledException
from order_fulfillment.service import ExchangeOrderFulfillmentService


class ExchangeOrdersMatchedHandler(KafkaConsumerHandler):

    _logger = get_logger(__name__)

    def __init__(self, order_fulfillment_service: ExchangeOrderFulfillmentService):
        self._order_fulfillment_service = order_fulfillment_service

    @kafka_consumer_handler(model=KafkaEvent[ExchangeMatchedOrderDto])
    async def handle_event(self, event: KafkaEvent[ExchangeMatchedOrderDto]):
        self._logger.info(f"[Buy Order ID: {event.data.buy.id}] [Sell Order ID: {event.data.sell.id}] Received matched exchange event")
        order = ExchangeMatchedOrderDtoToFulfillOrderDto.convert(event.data)
        try:
            await self._order_fulfillment_service.fulfill_orders(order)
        except OrderAlreadyFulfilledException:
            self._logger.warning(f"[Buy Order ID: {event.data.buy.id}] [Sell Order ID: {event.data.sell.id}] Order was already fulfilled. Discarding")


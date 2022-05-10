from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from common.configuration import ORDER_FULFILLED_TOPIC
from common.kafka.model import KafkaEvent
from common.kafka.producer import KafkaProducer
from common.logs import get_logger
from order_fulfillment.converter import FulfilledOrderToDtoFulfilledOrderDto, FulfillOrderDtoToFulfilledOrder
from order_fulfillment.error import OrderAlreadyFulfilledException
from order_fulfillment.models.dto import FulfilledOrderDto, FulfillOrderDto


class ExchangeOrderFulfillmentService(ABC):

    @abstractmethod
    async def fulfill_orders(self, order_to_fulfill: FulfillOrderDto) -> FulfilledOrderDto:
        pass


class MongoDbExchangeOrderFulfillmentService(ExchangeOrderFulfillmentService):

    _logger = get_logger(__name__)

    def __init__(self, mongo_client: AsyncIOMotorClient):
        self._mongo_client = mongo_client
        self._database = self._mongo_client.order_fullfilment
        self._collection = self._database.order_fulfillment

    async def fulfill_orders(self, order_to_fulfill: FulfillOrderDto) -> FulfilledOrderDto:
        key = {"_id": f"{order_to_fulfill.buy.id}{order_to_fulfill.sell.id}"}
        storage_object = FulfillOrderDtoToFulfilledOrder.convert(order_to_fulfill)
        try:
            await self._collection.insert_one(key, storage_object.dict())
        except DuplicateKeyError:
            raise OrderAlreadyFulfilledException(f"Order {key} has already been fulfilled")
        else:
            # TODO: Update balance of pending User Ledger and User Account service
            self._logger.info("Order has been fulfilled")
            return FulfilledOrderToDtoFulfilledOrderDto.convert(storage_object)


class KafkaNotificationExchangeOrderFulfillmentService(ExchangeOrderFulfillmentService):

    def __init__(self, order_fulfillment_service: ExchangeOrderFulfillmentService, kafka_producer: KafkaProducer):
        self._order_fulfillment_service = order_fulfillment_service
        self._kafka_producer = kafka_producer

    async def fulfill_orders(self, order_to_fulfill: FulfillOrderDto) -> FulfilledOrderDto:
        order = await self._order_fulfillment_service.fulfill_orders(order_to_fulfill)
        await self._kafka_producer.send(
            topic=ORDER_FULFILLED_TOPIC,
            event=KafkaEvent[FulfilledOrderDto](
                data=order
            )
        )
        return order

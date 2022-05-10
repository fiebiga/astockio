from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from common.configuration import ORDER_CREATED_TOPIC
from common.kafka.model import KafkaEvent
from common.kafka.producer import KafkaProducer
from orders.converter import CreateOrderDtoToOrder, OrderToOrderDto
from orders.models.dto import CreateOrderDto, OrderDto, OrderType, OrderStatus
from orders.models.storage import Order


class OrderService(ABC):

    @abstractmethod
    async def create_order(self, order: CreateOrderDto) -> OrderDto:
        pass

    @abstractmethod
    async def delete_order(self, order_id: UUID):
        pass

    @abstractmethod
    async def delete_all_orders(self):
        pass

    @abstractmethod
    async def update_order(self, order_id: UUID, status: OrderStatus):
        pass

    @abstractmethod
    async def get_orders(self, order_type: Optional[OrderType], ticker: Optional[str]) -> List[OrderDto]:
        pass

    @abstractmethod
    async def get_order(self, order_id: UUID) -> OrderDto:
        pass


class MongoDbOrderService(OrderService):

    def __init__(self, mongo_client: AsyncIOMotorClient):
        self._mongo_client = mongo_client
        self._database = self._mongo_client.orders
        self._table = self._database.orders

    async def create_order(self, order: CreateOrderDto) -> OrderDto:
        persistence_model = CreateOrderDtoToOrder.convert(
            source=order
        )
        self._table.insert_one(persistence_model.dict())
        return OrderToOrderDto.convert(persistence_model)

    async def delete_order(self, id: UUID):
        return self._table.delete_one({"_id": id})

    async def delete_all_orders(self):
        await self._table.drop()

    async def get_orders(self, order_type: Optional[OrderType], ticker: Optional[str]) -> List[OrderDto]:
        query_parameters = {}
        if order_type is not None:
            query_parameters["order_type"] = order_type
        if ticker is not None:
            query_parameters["ticker"] = ticker

        orders = await self._table.find(query_parameters).to_list(None)
        return list(map(lambda order: OrderToOrderDto.convert(Order(**order)), orders))

    async def get_order(self, order_id: UUID) -> OrderDto:
        order = await self._table.find_one({"_id": order_id})

        if order is None:
            raise Exception(f"Order {order_id} does not exist")

        return OrderToOrderDto.convert(Order(**order))

    async def update_order(self, order_id: UUID, status: OrderStatus):
        await self._table.update_one({"_id": order_id}, {"$set": {"status": status.value}})


class KafkaNotificationOrderService(OrderService):

    def __init__(self, order_service: OrderService, kafka_producer: KafkaProducer):
        self._order_service = order_service
        self._kafka_producer = kafka_producer

    async def create_order(self, order: CreateOrderDto) -> OrderDto:
        response = await self._order_service.create_order(order)
        await self._kafka_producer.send(
            topic=ORDER_CREATED_TOPIC,
            event=KafkaEvent[OrderDto](
                data=response
            )
        )
        return response

    async def delete_order(self, order_id: UUID):
        await self._order_service.delete_order(order_id)

    async def delete_all_orders(self):
        await self._order_service.delete_all_orders()

    async def get_orders(self, order_type: Optional[OrderType], ticker: Optional[str]) -> List[OrderDto]:
        return await self._order_service.get_orders(order_type=order_type, ticker=ticker)

    async def get_order(self, order_id: UUID) -> OrderDto:
        return await self._order_service.get_order(order_id)

    async def update_order(self, order_id: UUID, status: OrderStatus):
        await self._order_service.update_order(order_id=order_id, status=status)


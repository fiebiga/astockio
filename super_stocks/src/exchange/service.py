from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from uuid import UUID

from redis.asyncio import Redis

from common.configuration import ORDERS_MATCHED_TOPIC
from common.kafka.model import KafkaEvent
from common.kafka.producer import KafkaProducer
from exchange.models.dto import ExchangeOrderDto, ExchangeMatchedOrderDto


class ExchangeService(ABC):

    @abstractmethod
    async def submit_buy_order(self, order: ExchangeOrderDto):
        pass

    @abstractmethod
    async def submit_sell_order(self, order: ExchangeOrderDto):
        pass

    @abstractmethod
    async def consume_exchangeable_orders(self, ticker: str) -> List[ExchangeMatchedOrderDto]:
        pass


class RedisExchangeService(ExchangeService):

    # Execute in a LUA script for transactional atomic functionality. Peek at results, then pop if the results are favorable
    _HIGH_LOW_CALL_SCRIPT = """
    local sell_key = KEYS[1]
    local buy_key = KEYS[2]
    local sell_result = redis.call("ZRANGE", sell_key, 0, 0, "WITHSCORES")
    local buy_result = redis.call("ZRANGE", buy_key, 0, 0, "REV", "WITHSCORES")
    
    if #sell_result > 1 and #buy_result > 1 then
        if tonumber(sell_result[2]) <= tonumber(buy_result[2]) then
            local sell_pop = redis.call("ZPOPMIN", sell_key)
            local buy_pop = redis.call("ZPOPMAX", buy_key)
            return {sell_pop, buy_pop}
        end
    end

    return {nil, nil}
    """

    _BUY_GROUP_KEY_TEMPLATE = "orders#buy#{ticker}"
    _SELL_GROUP_KEY_TEMPLATE = "orders#sell#{ticker}"

    # Date submitted is included to be a lexicographical tie breaker
    _ORDER_KEY_TEMPLATE = "{date_submitted}#{id}#{user_id}"

    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client
        self._script = self._redis_client.register_script(self._HIGH_LOW_CALL_SCRIPT)

    def _build_order_key(self, order_id: UUID, user_id: UUID) -> str:
        return self._ORDER_KEY_TEMPLATE.format(
            id=order_id,
            user_id=user_id,
            date_submitted=datetime.utcnow().isoformat()
        )

    async def _submit_order(self, key_template: str, order: ExchangeOrderDto):
        set_key = key_template.format(
            ticker=order.ticker
        )
        order_key = self._build_order_key(
            order_id=order.id,
            user_id=order.user_id
        )
        response = await self._redis_client.zadd(set_key, {order_key: order.amount})
        if response != 1:
            raise Exception("Unknown error attempting to submit order")
        return response

    async def submit_buy_order(self, order: ExchangeOrderDto):
        await self._submit_order(self._BUY_GROUP_KEY_TEMPLATE, order)

    async def submit_sell_order(self, order: ExchangeOrderDto):
        await self._submit_order(self._SELL_GROUP_KEY_TEMPLATE, order)

    async def consume_exchangeable_orders(self, ticker: str) -> List[ExchangeMatchedOrderDto]:
        sell_key = self._SELL_GROUP_KEY_TEMPLATE.format(
            ticker=ticker
        )
        buy_key = self._BUY_GROUP_KEY_TEMPLATE.format(
            ticker=ticker
        )

        results: List[ExchangeMatchedOrderDto] = []
        result = await self._script(keys=[sell_key, buy_key])
        while len(result) > 0:
            sell_result, buy_result = result
            sell_date, sell_id, sell_user_id = sell_result[0].decode("utf-8").split("#")
            buy_date, buy_id, buy_user_id = buy_result[0].decode("utf-8").split("#")
            exchange_object = ExchangeMatchedOrderDto(
                sell=ExchangeOrderDto(
                    id=sell_id,
                    ticker=ticker,
                    user_id=sell_user_id,
                    amount=sell_result[1]
                ),
                buy=ExchangeOrderDto(
                    id=buy_id,
                    ticker=ticker,
                    user_id=buy_user_id,
                    amount=buy_result[1]
                )
            )

            results.append(exchange_object)
            result = await self._script(keys=[sell_key, buy_key])
        return results


class KafkaNotificationExchangeService(ExchangeService):

    def __init__(self, exchange_service: ExchangeService, kafka_producer: KafkaProducer):
        self._exchange_service = exchange_service
        self._kafka_producer = kafka_producer

    async def submit_buy_order(self, order: ExchangeOrderDto):
        await self._exchange_service.submit_buy_order(order)

    async def submit_sell_order(self, order: ExchangeOrderDto):
        await self._exchange_service.submit_sell_order(order)

    async def consume_exchangeable_orders(self, ticker: str) -> List[ExchangeMatchedOrderDto]:
        orders = await self._exchange_service.consume_exchangeable_orders(ticker)
        for order in orders:
            await self._kafka_producer.send(
                topic=ORDERS_MATCHED_TOPIC,
                event=KafkaEvent[ExchangeMatchedOrderDto](
                    data=order
                )
            )
        return orders


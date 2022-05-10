from abc import ABC, abstractmethod
from functools import wraps
from typing import List, Type

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from common.kafka.model import KafkaEvent


class KafkaConsumerHandler(ABC):

    @abstractmethod
    async def handle_event(self, event: KafkaEvent):
        pass


def kafka_consumer_handler(model: Type[KafkaEvent]):
    def real_decorator(function):
        @wraps(function)
        def wrapper(self, event: ConsumerRecord):
            data = model.parse_raw(event.value)
            return function(self, data)

        return wrapper

    return real_decorator


class KafkaConsumer:

    def __init__(self, bootstrap_servers: str = "localhost"):
        self._bootstrap_servers = bootstrap_servers
        self._handlers: List[KafkaConsumerHandler] = []

    def register_handler(self, handler: KafkaConsumerHandler):
        self._handlers.append(handler)

    async def consume(self, topic: str, auto_offset_reset: str = "latest"):
        if len(self._handlers) == 0:
            raise Exception("At least one consumer event handler is required")

        print(f"Connecting to {self._bootstrap_servers}")
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self._bootstrap_servers,
            auto_offset_reset=auto_offset_reset
        )
        await consumer.start()

        async for event in consumer:
            for handler in self._handlers:
                await handler.handle_event(event)
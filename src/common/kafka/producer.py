import asyncio

from aiokafka import AIOKafkaProducer

from common.kafka.model import KafkaEvent
from common.logs import get_logger


class KafkaProducer:

    _logger = get_logger(__name__)

    def __init__(self, bootstrap_servers: str = "localhost"):
        self._bootstrap_servers = bootstrap_servers

    async def send(self, topic: str, event: KafkaEvent):
        loop = asyncio.get_event_loop()
        producer = AIOKafkaProducer(loop=loop, bootstrap_servers=self._bootstrap_servers)
        await producer.start()

        message = event.json()
        try:
            await producer.send_and_wait(topic, message.encode("utf-8"))
            self._logger.info(f"[Topic: {topic}] Sent {message}")
        finally:
            await producer.stop()

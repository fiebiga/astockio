from redis.asyncio import Redis

from common.configuration import KAFKA_BOOTSTRAP_SERVERS
from common.kafka.consumer import KafkaConsumer
from common.kafka.producer import KafkaProducer
from exchange.handlers import OrderCreatedHandler
from exchange.service import ExchangeService, RedisExchangeService, KafkaNotificationExchangeService

exchange_service: ExchangeService = KafkaNotificationExchangeService(
    exchange_service=RedisExchangeService(
        redis_client=Redis()
    ),
    kafka_producer=KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
)

consumer = KafkaConsumer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

consumer.register_handler(
    OrderCreatedHandler(
        exchange_service=exchange_service
    )
)
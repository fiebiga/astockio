from motor.motor_asyncio import AsyncIOMotorClient

from common.configuration import KAFKA_BOOTSTRAP_SERVERS, MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD
from common.kafka.consumer import KafkaConsumer
from common.kafka.producer import KafkaProducer
from orders.handlers import OrderFulfilledEventHandler
from orders.service import OrderService, MongoDbOrderService, KafkaNotificationOrderService

mongo_client = AsyncIOMotorClient(
    MONGODB_HOST,
    MONGODB_PORT,
    username=MONGODB_USERNAME,
    password=MONGODB_PASSWORD,
    tz_aware=True,
    uuidRepresentation="standard"
)

order_service: OrderService = KafkaNotificationOrderService(
    MongoDbOrderService(
        mongo_client=mongo_client
    ),
    kafka_producer=KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
)

consumer = KafkaConsumer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

consumer.register_handler(
    OrderFulfilledEventHandler(
        order_service=order_service
    )
)

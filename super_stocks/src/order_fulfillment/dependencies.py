from motor.motor_asyncio import AsyncIOMotorClient

from common.configuration import KAFKA_BOOTSTRAP_SERVERS, MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD
from common.kafka.consumer import KafkaConsumer
from common.kafka.producer import KafkaProducer
from order_fulfillment.handlers import ExchangeOrdersMatchedHandler
from order_fulfillment.service import ExchangeOrderFulfillmentService, MongoDbExchangeOrderFulfillmentService, \
    KafkaNotificationExchangeOrderFulfillmentService

mongo_client = AsyncIOMotorClient(
    MONGODB_HOST,
    MONGODB_PORT,
    username=MONGODB_USERNAME,
    password=MONGODB_PASSWORD,
    tz_aware=True,
    uuidRepresentation="standard"
)

order_fulfillment_service: ExchangeOrderFulfillmentService = KafkaNotificationExchangeOrderFulfillmentService(
    order_fulfillment_service=MongoDbExchangeOrderFulfillmentService(
        mongo_client=mongo_client
    ),
    kafka_producer=KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
)

consumer = KafkaConsumer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

consumer.register_handler(
    ExchangeOrdersMatchedHandler(
        order_fulfillment_service=order_fulfillment_service
    )
)
import os

# Order Service Topics
ORDER_CREATED_TOPIC: str = "orders-order_created"
ORDER_UPDATED_TOPIC: str = "orders-order_updated"

# Exchange Service Topics
ORDERS_MATCHED_TOPIC: str = "exchange-orders_matched"

# Order Fulfillment Topics
ORDER_FULFILLED_TOPIC: str = "order-fulfillment-order_fulfilled"


# Mongo Configuration
MONGODB_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGODB_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGODB_USERNAME = os.environ.get("MONGO_USER", "sandbox_user")
MONGODB_PASSWORD = os.environ.get("MONGO_PASSWORD", "sandbox_password")

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost")
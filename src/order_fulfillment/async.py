import asyncio

from common.configuration import ORDERS_MATCHED_TOPIC
from order_fulfillment.dependencies import consumer

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(consumer.consume(ORDERS_MATCHED_TOPIC))
    finally:
        loop.close()

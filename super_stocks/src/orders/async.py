import asyncio

from common.configuration import ORDER_FULFILLED_TOPIC
from orders.dependencies import consumer

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(consumer.consume(ORDER_FULFILLED_TOPIC))
    finally:
        loop.close()

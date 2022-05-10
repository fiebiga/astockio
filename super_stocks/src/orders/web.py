import os

from typing import Optional, List
from uuid import UUID

from fastapi import FastAPI, Body


from orders.dependencies import order_service
from orders.models.dto import OrderType, OrderDto, CreateOrderDto

_ROOT_PATH = os.environ.get("WEB_ROOT", "/")


tags_metadata = [
    {
        "name": "orders",
        "description": "All operations related to placing an order to the stock exchange",
    }
]

app = FastAPI(
    root_path=_ROOT_PATH,
    openapi_tags=tags_metadata
)


@app.get("/orders", response_model=List[OrderDto], tags=["orders"])
async def get_orders(ticker: Optional[str] = None, order_type: Optional[OrderType] = None):
    return await order_service.get_orders(ticker=ticker, order_type=order_type)

@app.get("/orders/{id}", response_model=OrderDto, tags=["orders"])
async def get_order(id: UUID):
    return await order_service.get_order(id)

@app.delete("/orders", tags=["orders"])
async def delete_all_orders():
    await order_service.delete_all_orders()


@app.delete("/orders/{id}", tags=["orders"])
async def delete_order(id: UUID):
    return await order_service.delete_order(id)


@app.post("/orders", response_model=OrderDto, tags=["orders"])
async def create_order(order: CreateOrderDto = Body(...)):
    return await order_service.create_order(order)
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class TransactionType(str, Enum):
    sell = "sell"
    buy = "buy"
    hold = "hold"
    release_hold = "release_hold"


class UserStockTransactionDto(BaseModel):
    transaction_date: datetime
    type: TransactionType
    ticker: str
    adjustment: UUID
    available_after: float
    held_after: float
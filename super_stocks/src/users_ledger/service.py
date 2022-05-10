from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from redis.asyncio import Redis

from users_ledger.models.dto import UserStockTransactionDto


class UsersLedgerService(ABC):

    @abstractmethod
    async def update_stock(self, user_id: UUID, ticker: str, amount: float):
        pass

    @abstractmethod
    async def hold_stock(self, user_id: UUID, ticker: str, amount: float):
        pass

    @abstractmethod
    async def release_held_stock(self, user_id: UUID, ticker: str, amount: float):
        pass

    @abstractmethod
    async def trade_stock(self, source_user_id: UUID, ticker: str, amount: float, destination_user_id: UUID):
        pass

    @abstractmethod
    async def get_all_transactions(self, user_id: UUID) -> List[UserStockTransactionDto]:
        pass


class RedisUsersLedgerService(UsersLedgerService):

    _USER_STOCK_KEY = "user#{user_id}#stocks"

    _UPDATE_SCRIPT = """
    local key = KEYS[1]
    local ticker = KEYS[2]
    local amount = KEYS[3]
    
    local current_value = redis.call("ZSCORE", key, ticker)
    if current_value != nil then
        return 55
    end
    
    return 11
    """

    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client
        self._update_script = self._redis_client.register_script(self._UPDATE_SCRIPT)

    async def update_stock(self, user_id: UUID, ticker: str, amount: float):
        raise NotImplementedError()

    async def hold_stock(self, user_id: UUID, ticker: str, amount: float):
        raise NotImplementedError()

    async def release_held_stock(self, user_id: UUID, ticker: str, amount: float):
        raise NotImplementedError()

    async def trade_stock(self, source_user_id: UUID, ticker: str, amount: float, destination_user_id: UUID):
        raise NotImplementedError()

    async def get_all_transactions(self, user_id: UUID) -> List[UserStockTransactionDto]:
        raise NotImplementedError()



from redis.asyncio import Redis

from users_ledger.service import RedisUsersLedgerService, UsersLedgerService


users_ledger_service: UsersLedgerService = RedisUsersLedgerService(
    redis_client=Redis()
)

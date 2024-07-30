"""Repository for work callbacks with redis."""

import asyncio
import pickle  # noqa: S403
from typing import Optional
from uuid import UUID

# from redis import asyncio as aioredis  # type: ignore
import aioredis
from pybotx import CallbackNotReceivedError, CallbackRepoProto
from pybotx.models.method_callbacks import BotXMethodCallback

from app.resources import strings


class CallbackRedisRepo(CallbackRepoProto):
    CACHE_KEY = f"{strings.BOT_PROJECT_NAME}:callbacks_stream"
    CHECK_CALLBACKS_DELAY = 0.01

    def __init__(self, redis: aioredis.Redis, prefix: Optional[str] = None):
        self._redis = redis
        self._prefix = prefix or ""

    async def create_botx_method_callback(self, sync_id: UUID) -> None:
        """Unnecessary in streams implementation."""

    async def set_botx_method_callback_result(
        self, callback: BotXMethodCallback
    ) -> None:
        dump = pickle.dumps(callback)
        await self._redis.xadd(
            self.CACHE_KEY,
            {f"{self._prefix}:{callback.sync_id}": dump},
        )

    async def wait_botx_method_callback(
        self, sync_id: UUID, timeout: float
    ) -> BotXMethodCallback:
        try:
            callback = await asyncio.wait_for(
                self._wait_callback(sync_id), timeout=timeout
            )
        except asyncio.TimeoutError:
            raise CallbackNotReceivedError(sync_id) from None

        return callback

    async def pop_botx_method_callback(
        self, sync_id: UUID
    ) -> "asyncio.Future[BotXMethodCallback]":
        return await self._get_callback(self._get_callback_uid(sync_id))  # type: ignore

    async def stop_callbacks_waiting(self) -> None:
        await self._redis.delete(self.CACHE_KEY)

    async def _wait_callback(self, sync_id: UUID) -> BotXMethodCallback:
        callback_uid = self._get_callback_uid(sync_id)
        while True:
            callback = await self._get_callback(callback_uid)

            if callback:
                return callback

            await asyncio.sleep(self.CHECK_CALLBACKS_DELAY)

    async def _get_callback(self, callback_uid: bytes) -> Optional[BotXMethodCallback]:
        for cid, callback in await self._redis.xrange(self.CACHE_KEY):
            if callback_uid not in callback:
                continue

            await self._redis.xdel(self.CACHE_KEY, cid)
            return pickle.loads(callback[callback_uid])  # noqa: S301

        return None

    def _get_callback_uid(self, sync_id: UUID) -> bytes:
        return f"{self._prefix}:{sync_id}".encode()

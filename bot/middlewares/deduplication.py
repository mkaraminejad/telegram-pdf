"""Telegram Update Deduplication Middleware for Aiogram 3.

Prevents processing the same update multiple times in case of Telegram network retries.
Uses Redis with in-memory LRU fallback.
"""
import time
from typing import Callable, Dict, Any, Awaitable
from collections import OrderedDict
from aiogram import BaseMiddleware
from aiogram.types import Update
import redis.asyncio as aioredis
import logging

from bot.config import settings

logger = logging.getLogger(__name__)


class UpdateDeduplicationMiddleware(BaseMiddleware):
    """Rejects duplicate Telegram updates."""

    def __init__(self, redis_client: aioredis.Redis = None, ttl_seconds: int = 600):
        super().__init__()
        self.redis = redis_client
        self.ttl = ttl_seconds
        self._memory_cache: OrderedDict[int, float] = OrderedDict()
        self._max_cache_size = 5000

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        update_id = event.update_id

        # 1. Check Redis if connected
        if self.redis:
            try:
                key = f"tg_update:{update_id}"
                is_new = await self.redis.set(key, "1", ex=self.ttl, nx=True)
                if not is_new:
                    logger.warning("Duplicate Telegram update %d ignored (Redis)", update_id)
                    return None
            except Exception as e:
                logger.debug("Redis deduplication fallback to in-memory: %s", e)
                if not self._check_memory(update_id):
                    return None
        else:
            if not self._check_memory(update_id):
                return None

        return await handler(event, data)

    def _check_memory(self, update_id: int) -> bool:
        """In-memory cache fallback."""
        now = time.time()

        # Evict old entries
        while self._memory_cache and (now - next(iter(self._memory_cache.values()))) > self.ttl:
            self._memory_cache.popitem(last=False)

        if update_id in self._memory_cache:
            logger.warning("Duplicate Telegram update %d ignored (Memory)", update_id)
            return False

        if len(self._memory_cache) >= self._max_cache_size:
            self._memory_cache.popitem(last=False)

        self._memory_cache[update_id] = now
        return True

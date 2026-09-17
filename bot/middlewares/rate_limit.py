"""Per-User Rate Limiting Middleware for Aiogram 3.

Restricts excessive requests per user to protect system resources and worker queues.
Returns friendly Persian notification when the rate limit threshold is exceeded.
"""
import time
from typing import Callable, Dict, Any, Awaitable
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import Message
import redis.asyncio as aioredis
import logging

from bot.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Rate limits messages per user per minute."""

    def __init__(self, redis_client: aioredis.Redis = None, limit: int = None, window: int = 60):
        super().__init__()
        self.redis = redis_client
        self.limit = limit or settings.RATE_LIMIT_PER_MINUTE
        self.window = window
        self._memory_buckets: Dict[int, list] = defaultdict(list)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Only rate-limit private messages from users
        if not event.from_user or event.chat.type != "private":
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.time()
        is_limited = False

        if self.redis:
            try:
                key = f"rate_limit:{user_id}"
                pipe = self.redis.pipeline()
                pipe.zadd(key, {str(now): now})
                pipe.zremrangebyscore(key, 0, now - self.window)
                pipe.zcard(key)
                pipe.expire(key, self.window)
                _, _, count, _ = await pipe.execute()

                if count > self.limit:
                    is_limited = True
            except Exception as e:
                logger.debug("Redis rate limiter fallback to memory: %s", e)
                is_limited = self._check_memory(user_id, now)
        else:
            is_limited = self._check_memory(user_id, now)

        if is_limited:
            logger.warning("User %d exceeded rate limit of %d/min", user_id, self.limit)
            await event.answer(
                "⚠️ شما بیش از حد مجاز در دقیقه پیام ارسال کرده‌اید.\n"
                "لطفاً یک دقیقه صبر کنید و مجدداً تلاش فرمایید."
            )
            return None

        return await handler(event, data)

    def _check_memory(self, user_id: int, now: float) -> bool:
        """In-memory sliding window rate limiter fallback."""
        timestamps = self._memory_buckets[user_id]
        # Remove timestamps outside window
        self._memory_buckets[user_id] = [t for t in timestamps if now - t < self.window]

        if len(self._memory_buckets[user_id]) >= self.limit:
            return True

        self._memory_buckets[user_id].append(now)
        return False

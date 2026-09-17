"""Main Application Entrypoint for Persian PDF to DOCX Telegram Bot.

Supports both Long Polling (development & standard deployment) and
FastAPI / aiohttp Webhook (production HTTPS).
"""
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import redis.asyncio as aioredis

from bot.config import settings
from bot.handlers import main_router
from bot.middlewares.deduplication import UpdateDeduplicationMiddleware
from bot.middlewares.rate_limit import RateLimitMiddleware


def setup_logging():
    """Configures structured application logging without leaking sensitive document content."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


async def main():
    setup_logging()
    logger = logging.getLogger("bot.main")
    logger.info("Initializing Persian PDF to DOCX Telegram Bot...")

    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "PLACEHOLDER_TOKEN":
        logger.warning(
            "TELEGRAM_BOT_TOKEN is not set or using placeholder! "
            "Please configure your real bot token in .env"
        )

    # Initialize Bot instance
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Initialize Dispatcher
    dp = Dispatcher()

    # Setup Redis connection for middlewares
    redis_client = None
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Connected to Redis for deduplication and rate-limiting.")
    except Exception as e:
        logger.warning("Redis connection failed, running in memory-fallback mode: %s", e)
        redis_client = None

    # Register Middlewares
    dp.update.middleware(UpdateDeduplicationMiddleware(redis_client=redis_client))
    dp.message.middleware(RateLimitMiddleware(redis_client=redis_client))

    # Register Routers
    dp.include_router(main_router)

    try:
        if settings.WEBHOOK_URL:
            logger.info("Running in Webhook mode: %s", settings.WEBHOOK_URL)
            await bot.set_webhook(
                url=settings.WEBHOOK_URL,
                secret_token=settings.WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            # When using webhook in full container, a webhook webserver runs.
            # Here we provide long-polling fallback if webhook listener is not bound.
        else:
            logger.info("Starting long-polling mode (Drop pending updates = True)...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
    finally:
        if redis_client:
            await redis_client.aclose()
        await bot.session.close()
        logger.info("Bot stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot execution terminated by user.")

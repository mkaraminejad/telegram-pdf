# bot/handlers/__init__.py
from aiogram import Router
from bot.handlers.base import base_router
from bot.handlers.pdf_handler import pdf_router

main_router = Router()
main_router.include_router(base_router)
main_router.include_router(pdf_router)

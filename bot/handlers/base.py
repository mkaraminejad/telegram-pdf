"""Base Bot Handlers: /start, /help, /status, and Group Chat Guard."""
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.config import settings

logger = logging.getLogger(__name__)
base_router = Router()


@base_router.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_message(message: Message):
    """Guards against group chats; informs users to use private messages."""
    await message.reply(
        "👋 سلام! این ربات برای حفظ حریم خصوصی اسناد، فقط در چت خصوصی (PV) فعالیت می‌کند.\n"
        "لطفاً به پیوی ربات مراجعه کنید و فایل PDF خود را ارسال فرمایید."
    )


@base_router.message(CommandStart())
async def handle_start(message: Message):
    """Handles /start command with user-friendly Persian greeting."""
    welcome_text = (
        "سلام! به ربات تبدیل PDF فارسی به Word خوش آمدید. 📄➡️📝\n\n"
        "«فایل PDF فارسی خود را بفرستید تا نسخه Word آن را دریافت کنید.»\n\n"
        "✨ ویژگی‌های ربات:\n"
        "• پشتیبانی کامل از متن راست‌به‌چپ (RTL) و فونت‌های فارسی\n"
        "• حفظ نیم‌فاصله، اعداد فارسی و کلمات انگلیسی ترکیبی\n"
        "• OCR خودکار برای فایل‌های اسکن‌شده\n"
        "• حفظ حریم خصوصی و حذف خودکار فایل‌ها\n\n"
        "برای مشاهده نکات بیشتر دستور /help را ارسال کنید."
    )
    await message.answer(welcome_text)


@base_router.message(Command("help"))
async def handle_help(message: Message):
    """Handles /help command with instructions and operational limits."""
    help_text = (
        "💡 **راهنمای استفاده از ربات تبدیل PDF به Word:**\n\n"
        "۱. فایل PDF مورد نظر خود را به عنوان فایل (Document) در چت ارسال فرمایید.\n"
        f"۲. سقف مجاز حجم هر فایل: **{settings.MAX_FILE_SIZE_MB} مگابایت**\n"
        f"۳. سقف مجاز صفحات هر سند: **{settings.MAX_PAGE_COUNT} صفحه**\n"
        "۴. سیستم به صورت هوشمند نوع سند را تشخیص می‌دهد:\n"
        "   - **متن‌محور:** استخراج مستقیم و ساختاریافته.\n"
        "   - **اسکن‌شده:** پردازش با موتور OCR فارسی Tesseract.\n"
        "۵. خروجی در قالب فایل استاندارد `.docx` همراه با متادیتا و خصوصیات RTL تولید می‌شود.\n"
        "۶. تمامی فایل‌های موقت حداکثر تا ۲۴ ساعت به طور خودکار پاکسازی می‌شوند."
    )
    await message.answer(help_text, parse_mode="Markdown")


@base_router.message(Command("status"))
async def handle_status(message: Message):
    """Handles /status command to check system health."""
    status_text = (
        "🟢 **وضعیت سامانه تبدیل PDF به Word:**\n\n"
        "• وضعیت ربات: آنلاین و آماده دریافت فایل\n"
        "• صف پردازش پردازش ناهمگام (Celery): فعال\n"
        f"• زبان موتور OCR: {settings.TESSERACT_LANG}\n"
        f"• محدودیت حجم فایل: {settings.MAX_FILE_SIZE_MB} MB\n"
        f"• محدودیت صفحات: {settings.MAX_PAGE_COUNT} صفحه\n"
        f"• مدت زمان نگهداری فایل: حداکثر {settings.TEMP_FILE_TTL_HOURS} ساعت"
    )
    await message.answer(status_text, parse_mode="Markdown")

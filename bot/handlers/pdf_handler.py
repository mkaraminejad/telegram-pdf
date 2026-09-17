"""PDF Ingestion and Validation Handler.

Handles document uploads, enforces format and size constraints, downloads files
into isolated temporary storage, and enqueues Celery background tasks.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message

from bot.config import settings
from bot.services.storage import storage
from bot.tasks.celery_worker import convert_pdf_task

logger = logging.getLogger(__name__)
pdf_router = Router()


@pdf_router.message(F.document)
async def handle_document_upload(message: Message, bot: Bot):
    """Validates incoming document and dispatches conversion task to Celery queue."""
    document = message.document
    filename = document.file_name or "document.pdf"
    file_size = document.file_size or 0

    # 1. Validate File Extension and MIME
    is_pdf = filename.lower().endswith(".pdf") or document.mime_type == "application/pdf"
    if not is_pdf:
        await message.reply(
            "⚠️ لطفاً تنها فایل با فرمت PDF ارسال نمایید.\n"
            "سایر فرمت‌های ارسالی (تصویر، ویدیو، zip و غیره) پشتیبانی نمی‌شوند."
        )
        return

    # 2. Validate File Size
    if file_size > settings.max_file_size_bytes:
        size_mb = round(file_size / (1024 * 1024), 1)
        await message.reply(
            f"❌ حجم فایل ارسالی شما ({size_mb} مگابایت) بیش از سقف مجاز است.\n"
            f"حداکثر حجم مجاز: **{settings.MAX_FILE_SIZE_MB} مگابایت**",
            parse_mode="Markdown"
        )
        return

    # 3. Create isolated workspace for this task
    task_id, task_dir = storage.create_task_workspace()
    safe_filename = storage.sanitize_filename(filename)
    target_path = task_dir / safe_filename

    # 4. Immediate user acknowledgement
    ack_msg = await message.reply("⏳ فایل دریافت شد؛ در حال تبدیل…")

    try:
        # 5. Download file from Telegram servers
        file_info = await bot.get_file(document.file_id)
        if not file_info.file_path:
            raise ValueError("Could not obtain file path from Telegram API.")

        await bot.download_file(file_info.file_path, destination=target_path)
        logger.info("Downloaded %s (%d bytes) for task %s", filename, file_size, task_id)

        # 6. Dispatch async processing job to Celery / Redis queue
        convert_pdf_task.delay(
            task_id=task_id,
            chat_id=message.chat.id,
            original_filename=filename,
            pdf_path=str(target_path)
        )

    except Exception as e:
        logger.exception("Error downloading or dispatching task %s: %s", task_id, e)
        storage.cleanup_task(task_id)
        await message.reply(
            "⚠️ متأسفانه در دریافت فایل خطایی رخ داد.\n"
            "لطفاً مجدداً تلاش نمایید."
        )


@pdf_router.message(F.photo | F.video | F.audio | F.voice | F.sticker)
async def handle_invalid_media(message: Message):
    """Politely informs the user when media other than PDF document is sent."""
    await message.reply(
        "ℹ️ لطفاً سند خود را به صورت **فایل (Document)** با پسوند `.pdf` ارسال فرمایید.",
        parse_mode="Markdown"
    )


@pdf_router.message(F.text & ~F.text.startswith("/"))
async def handle_plain_text(message: Message):
    """Guides the user when plain text message is sent."""
    await message.reply(
        "📄 جهت تبدیل، لطفاً یک فایل PDF ارسال نمایید.\n"
        "برای راهنمای بیشتر دستور /help را لمس کنید."
    )

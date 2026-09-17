"""Celery Worker Tasks for PDF to DOCX Processing.

Executes asynchronous PDF extraction, OCR, RTL/BiDi normalization, DOCX generation,
Telegram document delivery, and automatic 24-hour cleanup.
"""
import os
import urllib.request
import urllib.parse
import json
import logging
from pathlib import Path

from bot.tasks.celery_app import celery_app
from bot.services.pdf_extractor import (
    PDFExtractor,
    PDFEncryptedError,
    PDFPageLimitExceededError,
    PDFCorruptError
)
from bot.services.docx_builder import DocxBuilder
from bot.services.storage import storage
from bot.config import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id: int, text: str) -> None:
    """Helper to send text notification to Telegram user."""
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        logger.error("Failed to send Telegram message to %s: %s", chat_id, e)


def send_telegram_document(chat_id: int, file_path: str, caption: str) -> bool:
    """Helper to upload and send generated DOCX document to Telegram chat."""
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    filename = os.path.basename(file_path)
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
        f"Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status == 200
    except Exception as e:
        logger.error("Failed to upload document to Telegram chat %s: %s", chat_id, e)
        return False


@celery_app.task(bind=True, max_retries=1, default_retry_delay=5)
def convert_pdf_task(
    self,
    task_id: str,
    chat_id: int,
    original_filename: str,
    pdf_path: str
):
    """Asynchronous Celery task to process PDF and generate RTL Word document."""
    logger.info("Starting conversion task %s for user %s", task_id, chat_id)
    docx_path = None

    try:
        # Step 1: Initialize Extractor and extract content
        extractor = PDFExtractor(
            max_pages=settings.MAX_PAGE_COUNT,
            ocr_dpi=settings.OCR_DPI
        )

        result = extractor.inspect_and_extract(pdf_path)

        # Step 2: Build DOCX with native RTL OpenXML
        output_name = Path(original_filename).stem + ".docx"
        task_dir = storage.get_task_workspace(task_id)
        docx_path = str(task_dir / output_name)

        builder = DocxBuilder()
        builder.build_from_extracted_content(result.pages_content, docx_path)

        # Step 3: Send converted DOCX to Telegram user
        caption = (
            "✅ فایل Word با موفقیت ساخته شد.\n\n"
            f"📄 تعداد صفحات: {result.total_pages}\n"
        )
        if getattr(result, "is_ai_powered", False):
            caption += "🤖 پردازش: هوش مصنوعی چندوجهی (Gemini Multimodal)\n"
            caption += "✨ رفع کامل وارونگی کلمات، اتصال حروف و ساختاردهی جداول و تیترها"
        elif result.is_scanned:
            caption += "🔍 نوع سند: اسکن‌شده (با OCR استخراج شد)\n"
            caption += "⚠️ برای فایل‌های اسکن‌شده یا جدول‌های پیچیده، بازبینی نهایی توصیه می‌شود."
        else:
            caption += "📝 نوع سند: متن‌محور (استخراج مستقیم و حفظ ساختار)"

        send_telegram_document(chat_id, docx_path, caption)
        logger.info("Successfully completed task %s and delivered DOCX", task_id)

    except PDFEncryptedError:
        send_telegram_message(
            chat_id,
            "🔒 این فایل PDF دارای رمز عبور است.\n"
            "لطفاً نسخه رمزگشایی‌شده (بدون رمز) را ارسال فرمایید."
        )
    except PDFPageLimitExceededError as e:
        send_telegram_message(
            chat_id,
            f"⚠️ {str(e)}\n"
            f"حداکثر سقف مجاز برای تبدیل، {settings.MAX_PAGE_COUNT} صفحه است."
        )
    except PDFCorruptError:
        send_telegram_message(
            chat_id,
            "❌ فایل ارسالی خراب یا غیرقابل‌خواندن است.\n"
            "لطفاً مطمئن شوید فایل PDF سالم است و مجدداً ارسال کنید."
        )
    except Exception as e:
        logger.exception("Unexpected error processing PDF for task %s: %s", task_id, e)
        send_telegram_message(
            chat_id,
            "⚠️ متأسفانه در حین تبدیل فایل خطایی رخ داد.\n"
            "تیم فنی در حال بررسی است. لطفاً فایل دیگری را امتحان کنید."
        )
    finally:
        # Immediate cleanup of temporary input files and generated docx
        storage.cleanup_task(task_id)


@celery_app.task
def purge_expired_files_task():
    """Periodic Celery task to purge leftover files older than 24 hours."""
    count = storage.purge_expired(max_age_hours=settings.TEMP_FILE_TTL_HOURS)
    logger.info("Purge job finished: removed %d expired directories.", count)
    return count

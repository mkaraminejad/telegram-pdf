"""AI-Powered Persian Document Extraction and Layout Understanding.

Leverages Google Gemini Multimodal Vision to eliminate reversed Persian characters,
restore disconnected letters, detect tables, headings, lists, and construct
high-fidelity Word documents in the background.
"""
import os
import json
import base64
import logging
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional

from bot.config import settings
from bot.services.normalizer import normalizer

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """شما یک دستیار تخصصی هوش مصنوعی برای استخراج، بازخوانی و ساختاردهی اسناد PDF و تصاویر متنی به زبان فارسی هستید.
وظیفه شما:
۱. بازخوانی دقیق متن فارسی بدون هرگونه وارونگی کلمات یا جداافتادگی حروف (مانند «س ل ا م» که باید به «سلام» تبدیل شود).
۲. تشخیص ساختار سند شامل: تیترها (heading با سطح ۱ تا ۳)، پاراگراف‌ها (paragraph)، لیست‌های نشانه‌دار یا شماره‌دار (bullet)، و جداول (table با آرایه سطرها و ستون‌ها).
۳. حفظ دقیق اصطلاحات انگلیسی، کدهای برنامه‌نویسی، آدرس‌های وب و اعداد بدون وارونگی جهت (BiDi).
۴. اصلاح نشانه‌گذاری فارسی (استفاده از « » برای گیومه، علامت سؤال فارسی ؟ و ویرگول فارسی ،).
۵. رعایت نیم‌فاصله‌های صحیح نگارشی (مانند «می‌رود»، «کتاب‌ها»، «خانه‌ام»).

پاسخ شما فقط و فقط باید یک آرایه JSON از بلوک‌های زیر باشد:
[
  {"type": "heading", "level": 1, "text": "عنوان سند یا بخش"},
  {"type": "paragraph", "text": "متن پاراگراف با رعایت زبان و راستا..."},
  {"type": "bullet", "text": "مورد اول از لیست"},
  {"type": "table", "data": [["ستون ۱", "ستون ۲"], ["مقدار ۱", "مقدار ۲"]]}
]
هیچ متن یا توضیح اضافی خارج از آرایه JSON ارسال نکنید.
"""


class GeminiAIExtractor:
    """Intelligent Persian document extractor using Google Gemini Multimodal Vision."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self.model = model or settings.AI_MODEL_NAME or "gemini-3.8-flash"

    def is_available(self) -> bool:
        """Checks if Gemini API key is configured and AI engine is enabled."""
        return bool(self.api_key and settings.USE_AI_ENGINE)

    def extract_page_structure(
        self,
        image_bytes: Optional[bytes] = None,
        fallback_raw_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Sends page image and/or text to Gemini AI for intelligent Persian layout extraction.

        Args:
            image_bytes: PNG/JPEG bytes of the rendered PDF page.
            fallback_raw_text: Raw extracted text as secondary hint if image isn't available.

        Returns:
            List of structured content blocks (heading, paragraph, bullet, table).
        """
        if not self.is_available():
            logger.warning("Gemini AI Engine is not available; falling back to local extractor.")
            return self._build_fallback_blocks(fallback_raw_text)

        try:
            parts = []

            # Add image part if available
            if image_bytes:
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": b64_img
                    }
                })

            # Add text prompt
            prompt_text = "لطفاً متن و ساختار این صفحه سند را دقیقاً بازخوانی و طبق دستورالعمل به صورت JSON ساختاریافته استخراج کنید."
            if fallback_raw_text and len(fallback_raw_text.strip()) > 0:
                prompt_text += f"\n\nمتن اولیه خام صفحه جهت کمک به تشخیص کلمات:\n{fallback_raw_text[:2000]}"

            parts.append({"text": prompt_text})

            # Call Gemini API via Google's official REST endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            
            payload = {
                "system_instruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                },
                "contents": [
                    {"parts": parts}
                ],
                "generation_config": {
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "aistudio-build"
                }
            )

            with urllib.request.urlopen(req, timeout=45) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

            # Extract generated content
            candidates = res_json.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini API")

            first_candidate = candidates[0]
            parts_output = first_candidate.get("content", {}).get("parts", [])
            if not parts_output:
                raise ValueError("Empty response parts from Gemini API")

            raw_answer = parts_output[0].get("text", "").strip()

            # Clean JSON markdown fences if present
            if raw_answer.startswith("```json"):
                raw_answer = raw_answer[7:]
            if raw_answer.startswith("```"):
                raw_answer = raw_answer[3:]
            if raw_answer.endswith("```"):
                raw_answer = raw_answer[:-3]
            raw_answer = raw_answer.strip()

            parsed_blocks = json.loads(raw_answer)

            # Sanitize and normalize blocks
            cleaned_blocks: List[Dict[str, Any]] = []
            if isinstance(parsed_blocks, list):
                for blk in parsed_blocks:
                    if not isinstance(blk, dict):
                        continue
                    b_type = blk.get("type", "paragraph")
                    if b_type == "table":
                        data = blk.get("data", [])
                        if isinstance(data, list) and len(data) > 0:
                            cleaned_data = []
                            for row in data:
                                if isinstance(row, list):
                                    cleaned_row = [normalizer.normalize(str(cell)) for cell in row]
                                    cleaned_data.append(cleaned_row)
                            cleaned_blocks.append({"type": "table", "data": cleaned_data})
                    elif b_type == "heading":
                        cleaned_blocks.append({
                            "type": "heading",
                            "level": int(blk.get("level", 1)),
                            "text": normalizer.normalize(str(blk.get("text", "")))
                        })
                    elif b_type == "bullet":
                        cleaned_blocks.append({
                            "type": "bullet",
                            "text": normalizer.normalize(str(blk.get("text", "")))
                        })
                    else:
                        cleaned_blocks.append({
                            "type": "paragraph",
                            "text": normalizer.normalize(str(blk.get("text", "")))
                        })

                if cleaned_blocks:
                    return cleaned_blocks

            return self._build_fallback_blocks(fallback_raw_text)

        except Exception as e:
            logger.error("Gemini AI extraction error: %s", e)
            return self._build_fallback_blocks(fallback_raw_text)

    def _build_fallback_blocks(self, raw_text: Optional[str]) -> List[Dict[str, Any]]:
        """Fallback block construction if AI call is unavailable or fails."""
        if not raw_text:
            return []

        blocks = []
        for paragraph in raw_text.split("\n\n"):
            p = paragraph.strip()
            if not p:
                continue
            norm = normalizer.normalize(p)
            if len(norm) < 80 and not norm.endswith((".", "!", "؟", "؛")):
                blocks.append({"type": "heading", "level": 2, "text": norm})
            elif norm.startswith(("-", "•", "*")):
                blocks.append({"type": "bullet", "text": norm.lstrip("-•* ")})
            else:
                blocks.append({"type": "paragraph", "text": norm})
        return blocks


# Singleton instance
ai_extractor = GeminiAIExtractor()

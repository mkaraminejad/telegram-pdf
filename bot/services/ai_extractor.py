"""AI-Powered Persian Document Extraction using Groq & Google Gemini.

Supports Groq (Llama 3.3 70B Versatile, Llama 3.2 Vision) and Google Gemini (gemini-3.8-flash)
for high-speed layout understanding, word de-scrambling, Persian OCR correction, and
Word document generation.
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
۱. بازخوانی دقیق متن فارسی بدون هرگونه وارونگی کلمات یا جداافتادگی حروف (مانند «س ل ا م» یا «ی ازمند ی ادگ ی ر ی» که باید به «نیازمند یادگیری» تبدیل شود).
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


class GroqAIExtractor:
    """Intelligent Persian document extractor using Groq API (Llama 3.3 70B / Llama 3.2 Vision)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        self.model = model or settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    def is_available(self) -> bool:
        """Checks if Groq API key is configured and AI engine is enabled."""
        return bool(self.api_key and settings.USE_AI_ENGINE)

    def extract_page_structure(
        self,
        image_bytes: Optional[bytes] = None,
        fallback_raw_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Sends content to Groq API using OpenAI-compatible endpoint."""
        if not self.is_available():
            return []

        try:
            url = "https://api.groq.com/openai/v1/chat/completions"

            # Determine whether to use vision or text mode
            is_vision_model = "vision" in self.model.lower()
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            prompt_text = "لطفاً متن این سند فارسی را که دارای شکستگی خطوط، جداشدن حروف و به‌هم‌ریختگی است، کاملاً اصلاح و به صورت JSON ساختاریافته استخراج کنید."
            if fallback_raw_text and len(fallback_raw_text.strip()) > 0:
                prompt_text += f"\n\nمتن خام استخراج‌شده از سند:\n{fallback_raw_text[:4000]}"

            if image_bytes and is_vision_model:
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                user_content = [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_img}"
                        }
                    }
                ]
                messages.append({"role": "user", "content": user_content})
            else:
                messages.append({"role": "user", "content": prompt_text})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "aistudio-build"
                }
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

            choices = res_json.get("choices", [])
            if not choices:
                return []

            raw_answer = choices[0].get("message", {}).get("content", "").strip()
            return _parse_json_blocks(raw_answer)

        except Exception as e:
            logger.error("Groq AI extraction error: %s", e)
            return []


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
        """Sends page image and/or text to Gemini AI for intelligent Persian layout extraction."""
        if not self.is_available():
            return []

        try:
            parts = []

            if image_bytes:
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": b64_img
                    }
                })

            prompt_text = "لطفاً متن و ساختار این صفحه سند را دقیقاً بازخوانی و طبق دستورالعمل به صورت JSON ساختاریافته استخراج کنید."
            if fallback_raw_text and len(fallback_raw_text.strip()) > 0:
                prompt_text += f"\n\nمتن اولیه خام صفحه جهت کمک به تشخیص کلمات:\n{fallback_raw_text[:3000]}"

            parts.append({"text": prompt_text})

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

            candidates = res_json.get("candidates", [])
            if not candidates:
                return []

            parts_output = candidates[0].get("content", {}).get("parts", [])
            if not parts_output:
                return []

            raw_answer = parts_output[0].get("text", "").strip()
            return _parse_json_blocks(raw_answer)

        except Exception as e:
            logger.error("Gemini AI extraction error: %s", e)
            return []


class UnifiedAIExtractor:
    """Unified AI extractor switching dynamically between Groq and Gemini."""

    def __init__(self):
        self.groq = GroqAIExtractor()
        self.gemini = GeminiAIExtractor()

    def is_available(self) -> bool:
        provider = (settings.AI_PROVIDER or "").lower()
        if provider == "groq":
            return self.groq.is_available()
        return self.gemini.is_available() or self.groq.is_available()

    def get_active_provider_name(self) -> str:
        provider = (settings.AI_PROVIDER or "").lower()
        if provider == "groq" and self.groq.is_available():
            return f"Groq ({settings.GROQ_MODEL})"
        if self.gemini.is_available():
            return f"Gemini ({settings.AI_MODEL_NAME})"
        if self.groq.is_available():
            return f"Groq ({settings.GROQ_MODEL})"
        return "None"

    def extract_page_structure(
        self,
        image_bytes: Optional[bytes] = None,
        fallback_raw_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        provider = (settings.AI_PROVIDER or "").lower()

        # Try Groq if selected or configured
        if provider == "groq" and self.groq.is_available():
            logger.info("Extracting document layout with Groq (%s)...", settings.GROQ_MODEL)
            blocks = self.groq.extract_page_structure(image_bytes, fallback_raw_text)
            if blocks:
                return blocks
            # Fallback to Gemini if Groq fails
            if self.gemini.is_available():
                logger.info("Groq returned empty, falling back to Gemini...")
                blocks = self.gemini.extract_page_structure(image_bytes, fallback_raw_text)
                if blocks:
                    return blocks

        # Default Gemini path
        if self.gemini.is_available():
            logger.info("Extracting document layout with Gemini (%s)...", settings.AI_MODEL_NAME)
            blocks = self.gemini.extract_page_structure(image_bytes, fallback_raw_text)
            if blocks:
                return blocks

        # Try Groq if Gemini wasn't available
        if self.groq.is_available():
            logger.info("Extracting document layout with Groq (%s)...", settings.GROQ_MODEL)
            blocks = self.groq.extract_page_structure(image_bytes, fallback_raw_text)
            if blocks:
                return blocks

        return self._build_fallback_blocks(fallback_raw_text)

    def _build_fallback_blocks(self, raw_text: Optional[str]) -> List[Dict[str, Any]]:
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


def _parse_json_blocks(raw_answer: str) -> List[Dict[str, Any]]:
    """Helper to parse and sanitize JSON blocks from LLM response."""
    if not raw_answer:
        return []

    # Clean markdown fences
    raw_answer = raw_answer.strip()
    if raw_answer.startswith("```json"):
        raw_answer = raw_answer[7:]
    if raw_answer.startswith("```"):
        raw_answer = raw_answer[3:]
    if raw_answer.endswith("```"):
        raw_answer = raw_answer[:-3]
    raw_answer = raw_answer.strip()

    try:
        data = json.loads(raw_answer)
        # Handle cases where LLM wraps in {"blocks": [...]} or returns list directly
        items = data if isinstance(data, list) else data.get("blocks", data.get("items", []))
        if not isinstance(items, list):
            return []

        cleaned: List[Dict[str, Any]] = []
        for blk in items:
            if not isinstance(blk, dict):
                continue
            b_type = blk.get("type", "paragraph")
            if b_type == "table":
                tdata = blk.get("data", [])
                if isinstance(tdata, list) and len(tdata) > 0:
                    cleaned_rows = []
                    for row in tdata:
                        if isinstance(row, list):
                            cleaned_rows.append([normalizer.normalize(str(c)) for c in row])
                    cleaned.append({"type": "table", "data": cleaned_rows})
            elif b_type == "heading":
                cleaned.append({
                    "type": "heading",
                    "level": int(blk.get("level", 1)),
                    "text": normalizer.normalize(str(blk.get("text", "")))
                })
            elif b_type == "bullet":
                cleaned.append({
                    "type": "bullet",
                    "text": normalizer.normalize(str(blk.get("text", "")))
                })
            else:
                cleaned.append({
                    "type": "paragraph",
                    "text": normalizer.normalize(str(blk.get("text", "")))
                })
        return cleaned
    except Exception as e:
        logger.warning("JSON parse error on AI response: %s", e)
        return []


# Singleton instances
ai_extractor = UnifiedAIExtractor()
groq_extractor = GroqAIExtractor()
gemini_extractor = GeminiAIExtractor()

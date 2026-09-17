"""PDF Extraction Engine.

Handles text-based extraction via PyMuPDF (fitz), detects scanned pages,
detects password encryption and page limits, and delegates scanned pages
to the OCR engine.
"""
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from bot.services.ocr_engine import BaseOCREngine, TesseractOCREngine
from bot.services.ai_extractor import ai_extractor, GeminiAIExtractor
from bot.config import settings

logger = logging.getLogger(__name__)


class PDFError(Exception):
    """Base exception for PDF processing errors."""
    pass


class PDFEncryptedError(PDFError):
    """Raised when PDF is password-protected or encrypted."""
    pass


class PDFPageLimitExceededError(PDFError):
    """Raised when PDF exceeds allowed page threshold."""
    pass


class PDFCorruptError(PDFError):
    """Raised when PDF is corrupt or invalid binary."""
    pass


@dataclass
class ExtractionResult:
    is_scanned: bool
    total_pages: int
    scanned_pages_count: int
    text_pages_count: int
    pages_content: List[Dict[str, Any]]
    is_ai_powered: bool = False


class PDFExtractor:
    """Intelligent PDF extractor capable of handling text-based and scanned Persian PDFs."""

    def __init__(
        self,
        ocr_engine: BaseOCREngine = None,
        max_pages: int = None,
        ocr_dpi: int = None
    ):
        self.ocr_engine = ocr_engine or TesseractOCREngine(lang=settings.TESSERACT_LANG)
        self.max_pages = max_pages or settings.MAX_PAGE_COUNT
        self.ocr_dpi = ocr_dpi or settings.OCR_DPI

    def inspect_and_extract(self, pdf_path: str) -> ExtractionResult:
        """Validates PDF constraints and extracts structured content from all pages."""
        if not fitz:
            raise RuntimeError("PyMuPDF (fitz) is not installed in the environment.")

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            logger.error("Failed to open PDF %s: %s", pdf_path, e)
            raise PDFCorruptError("فایل ارسالی خراب یا نامعتبر است.")

        try:
            # Check encryption
            if doc.is_encrypted:
                raise PDFEncryptedError("این فایل دارای رمز عبور است. لطفاً نسخه بدون رمز را ارسال کنید.")

            total_pages = len(doc)
            if total_pages == 0:
                raise PDFCorruptError("فایل PDF هیچ صفحه‌ای ندارد.")

            if total_pages > self.max_pages:
                raise PDFPageLimitExceededError(
                    f"تعداد صفحات فایل ({total_pages}) بیش از سقف مجاز ({self.max_pages} صفحه) است."
                )

            pages_content: List[Dict[str, Any]] = []
            scanned_pages_count = 0
            text_pages_count = 0

            for page_num in range(total_pages):
                page = doc[page_num]
                is_scanned_page, page_blocks = self._extract_page(page, page_num)

                if is_scanned_page:
                    scanned_pages_count += 1
                else:
                    text_pages_count += 1

                pages_content.append({
                    "page_number": page_num + 1,
                    "is_scanned": is_scanned_page,
                    "blocks": page_blocks
                })

            overall_scanned = scanned_pages_count > (total_pages / 2)

            return ExtractionResult(
                is_scanned=overall_scanned,
                total_pages=total_pages,
                scanned_pages_count=scanned_pages_count,
                text_pages_count=text_pages_count,
                pages_content=pages_content,
                is_ai_powered=ai_extractor.is_available()
            )

        finally:
            doc.close()

    def _extract_page(self, page: Any, page_num: int) -> Tuple[bool, List[Dict[str, Any]]]:
        """Extracts content from an individual page, determining whether to use AI Multimodal, direct extraction or OCR."""
        # Check raw text length
        raw_text = page.get_text("text").strip()
        has_images = len(page.get_images()) > 0

        # Heuristic: If text length is very low (< 40 characters) and has images or blank canvas, treat as scanned
        is_scanned = len(raw_text) < 40 and (has_images or len(raw_text) == 0)

        # 🌟 Primary Method: Google Gemini AI Multimodal Vision & Layout Restoration
        if ai_extractor.is_available():
            logger.info("Page %d: Utilizing Gemini AI Multimodal Vision for Persian document restoration...", page_num + 1)
            try:
                pix = page.get_pixmap(dpi=self.ocr_dpi)
                img_bytes = pix.tobytes("png")
                ai_blocks = ai_extractor.extract_page_structure(image_bytes=img_bytes, fallback_raw_text=raw_text)
                if ai_blocks and len(ai_blocks) > 0:
                    return is_scanned, ai_blocks
            except Exception as e:
                logger.warning("AI extraction failed on page %d, falling back to local extractor: %s", page_num + 1, e)

        # Fallback Method: Local PyMuPDF + Tesseract
        blocks: List[Dict[str, Any]] = []

        if is_scanned:
            logger.info("Page %d detected as scanned/image. Running OCR...", page_num + 1)
            # Render page to high-res image
            pix = page.get_pixmap(dpi=self.ocr_dpi)
            img_bytes = pix.tobytes("png")

            try:
                ocr_text = self.ocr_engine.extract_text(img_bytes)
                for paragraph in ocr_text.split('\n\n'):
                    paragraph = paragraph.strip()
                    if paragraph:
                        blocks.append({
                            "type": "paragraph",
                            "text": paragraph
                        })
            except Exception as e:
                logger.error("OCR failed on page %d: %s", page_num + 1, e)
                blocks.append({
                    "type": "paragraph",
                    "text": raw_text or "[خطا در بازخوانی OCR این صفحه]"
                })
        else:
            # Text-based page: Extract structural blocks
            # 1. Try extracting tables first
            table_rects = []
            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    for tab in tabs.tables:
                        table_data = tab.extract()
                        if table_data:
                            blocks.append({
                                "type": "table",
                                "data": table_data
                            })
                            table_rects.append(tab.bbox)
            except Exception as e:
                logger.debug("Table detection error on page %d: %s", page_num + 1, e)

            # 2. Extract text blocks and headings
            text_dict = page.get_text("dict")
            for b in text_dict.get("blocks", []):
                # If block overlaps an extracted table, skip to prevent duplicates
                b_bbox = b.get("bbox")
                if b_bbox and any(self._is_overlapping(b_bbox, t_rect) for t_rect in table_rects):
                    continue

                if b.get("type") == 0:  # Text block
                    block_text_lines = []
                    max_size = 0.0

                    for line in b.get("lines", []):
                        line_spans = []
                        for span in line.get("spans", []):
                            span_text = span.get("text", "")
                            line_spans.append(span_text)
                            if span.get("size", 0) > max_size:
                                max_size = span.get("size", 0)
                        block_text_lines.append("".join(line_spans))

                    block_text = "\n".join(block_text_lines).strip()
                    if not block_text:
                        continue

                    # Check if heading (font size > 14pt)
                    is_heading = max_size >= 14.0 and len(block_text) < 120
                    heading_level = 1 if max_size >= 18.0 else (2 if max_size >= 15.0 else 3)

                    # Check bullet points
                    is_bullet = block_text.startswith(('•', '-', '*', '–'))

                    if is_heading:
                        blocks.append({
                            "type": "heading",
                            "level": heading_level,
                            "text": block_text
                        })
                    elif is_bullet:
                        blocks.append({
                            "type": "bullet",
                            "text": block_text.lstrip('•-*– ').strip()
                        })
                    else:
                        blocks.append({
                            "type": "paragraph",
                            "text": block_text
                        })

        return is_scanned, blocks

    @staticmethod
    def _is_overlapping(bbox1, bbox2) -> bool:
        """Determines if two bounding boxes overlap."""
        return not (
            bbox1[2] <= bbox2[0] or
            bbox1[0] >= bbox2[2] or
            bbox1[3] <= bbox2[1] or
            bbox1[1] >= bbox2[3]
        )

"""Pluggable OCR Engine Interface and Tesseract Implementation.

Designed with an abstract interface (BaseOCREngine) so that alternative OCR engines
(e.g., EasyOCR, TrOCR, Surfer, or Cloud OCR) can be swapped in without modifying
the core pipeline.
"""
import io
import logging
from abc import ABC, abstractmethod
from typing import Optional, Union
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

logger = logging.getLogger(__name__)


class BaseOCREngine(ABC):
    """Abstract base class for Persian OCR engines."""

    @abstractmethod
    def extract_text(self, image: Union[Image.Image, bytes]) -> str:
        """Extracts text from an image.

        Args:
            image: PIL Image instance or raw image bytes.

        Returns:
            Extracted text string.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the OCR engine dependencies and models are loaded and ready."""
        pass


class TesseractOCREngine(BaseOCREngine):
    """Tesseract OCR implementation configured with Persian (fas) and English (eng) models."""

    def __init__(
        self,
        lang: str = "fas+eng",
        tesseract_cmd: Optional[str] = None,
        psm: int = 3,
        oem: int = 1
    ):
        self.lang = lang
        self.psm = psm
        self.oem = oem

        if tesseract_cmd and pytesseract:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def is_available(self) -> bool:
        """Verifies if Tesseract binary and models are accessible."""
        if not pytesseract:
            return False
        try:
            installed_langs = pytesseract.get_languages()
            return 'fas' in installed_langs or 'fa' in installed_langs
        except Exception as e:
            logger.warning("Tesseract check failed: %s", e)
            return False

    def extract_text(self, image: Union[Image.Image, bytes]) -> str:
        """Runs Tesseract OCR on a page image with optimized Persian config."""
        if not pytesseract:
            raise RuntimeError("pytesseract is not installed")

        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        config = f'--oem {self.oem} --psm {self.psm}'
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=config
            )
            return text.strip()
        except Exception as e:
            logger.error("OCR execution error: %s", e)
            raise RuntimeError(f"خطا در استخراج متن از تصویر: {str(e)}")


def get_ocr_engine(engine_name: str = "tesseract") -> BaseOCREngine:
    """Factory to instantiate the configured OCR engine."""
    if engine_name.lower() == "tesseract":
        return TesseractOCREngine()
    raise ValueError(f"Unknown OCR engine: {engine_name}")

"""Integration Tests for Persian PDF to DOCX Pipeline.

Tests:
1. End-to-end extraction and conversion of a text-based Persian PDF.
2. End-to-end extraction and OCR routing of a scanned Persian PDF.
"""
import unittest
import tempfile
import os
from PIL import Image, ImageDraw

from bot.services.pdf_extractor import PDFExtractor
from bot.services.ocr_engine import BaseOCREngine
from bot.services.docx_builder import DocxBuilder

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None


class MockPersianOCREngine(BaseOCREngine):
    """Mock OCR engine for deterministic test execution in test environments."""

    def is_available(self) -> bool:
        return True

    def extract_text(self, image) -> str:
        return (
            "متن بازخوانی شده از سند اسکن‌شده فارسی توسط OCR.\n\n"
            "این متن برای راستی‌آزمایی خط لوله پردازش اسناد تصویری تولید شده است."
        )


class TestPDFIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.text_pdf_path = os.path.join(self.temp_dir, "sample_text.pdf")
        self.scanned_pdf_path = os.path.join(self.temp_dir, "sample_scanned.pdf")
        self.output_docx_path = os.path.join(self.temp_dir, "output.docx")

    def tearDown(self):
        for path in [self.text_pdf_path, self.scanned_pdf_path, self.output_docx_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        if os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except OSError:
                pass

    @unittest.skipIf(fitz is None, "PyMuPDF not installed in local environment")
    def test_text_based_pdf_conversion(self):
        """Creates a real text-based PDF with Persian text and verifies direct extraction."""
        doc = fitz.open()
        page = doc.new_page()
        text_content = (
            "راهنمای جامع هوش مصنوعی و پردازش زبان طبیعی فارسی.\n"
            "این یک سند آزمایشی متنمحور است که توسط سیستم استخراج میشود."
        )
        # Insert text into page
        page.insert_text(fitz.Point(50, 72), text_content, fontsize=12)
        doc.save(self.text_pdf_path)
        doc.close()

        # Run extraction
        extractor = PDFExtractor(ocr_engine=MockPersianOCREngine())
        result = extractor.inspect_and_extract(self.text_pdf_path)

        self.assertEqual(result.total_pages, 1)
        self.assertFalse(result.is_scanned, "Text-based PDF should not be classified as scanned")
        self.assertEqual(result.text_pages_count, 1)

        # Build DOCX
        builder = DocxBuilder()
        builder.build_from_extracted_content(result.pages_content, self.output_docx_path)

        self.assertTrue(os.path.exists(self.output_docx_path))
        self.assertGreater(os.path.getsize(self.output_docx_path), 500)

    @unittest.skipIf(fitz is None, "PyMuPDF not installed in local environment")
    def test_scanned_pdf_conversion(self):
        """Creates an image-only (scanned) PDF and verifies OCR routing and DOCX generation."""
        # Create an image representing a scanned document
        img_path = os.path.join(self.temp_dir, "scan_page.png")
        img = Image.new('RGB', (800, 1100), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([(40, 40), (760, 1060)], outline=(200, 200, 200), width=2)
        img.save(img_path)

        # Insert into PDF as image page without text layer
        doc = fitz.open()
        page = doc.new_page(width=800, height=1100)
        page.insert_image(fitz.Rect(0, 0, 800, 1100), filename=img_path)
        doc.save(self.scanned_pdf_path)
        doc.close()

        if os.path.exists(img_path):
            os.remove(img_path)

        # Run extraction with Mock OCR engine
        extractor = PDFExtractor(ocr_engine=MockPersianOCREngine())
        result = extractor.inspect_and_extract(self.scanned_pdf_path)

        self.assertEqual(result.total_pages, 1)
        self.assertTrue(result.is_scanned, "Image-only PDF should be classified as scanned")
        self.assertEqual(result.scanned_pages_count, 1)

        # Ensure OCR text was captured
        page_blocks = result.pages_content[0]["blocks"]
        self.assertGreater(len(page_blocks), 0)
        self.assertIn("سند اسکن‌شده", page_blocks[0]["text"])

        # Build DOCX
        builder = DocxBuilder()
        builder.build_from_extracted_content(result.pages_content, self.output_docx_path)

        self.assertTrue(os.path.exists(self.output_docx_path))
        self.assertGreater(os.path.getsize(self.output_docx_path), 500)


if __name__ == "__main__":
    unittest.main()

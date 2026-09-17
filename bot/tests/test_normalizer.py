"""Unit Tests for Persian Text Normalization and BiDi engine.

Tests:
1. Arabic to Persian character conversion ('ي' and 'ك').
2. Half-space (ZWNJ / نیم‌فاصله) for verbs and plural suffixes.
3. Digits normalization (Arabic, English, Persian).
4. Mixed Persian-English text preservation without reversal.
5. URL and code protection.
6. Punctuation standardization.
7. Multiline text normalization and spacing.
"""
import unittest
from bot.services.normalizer import PersianNormalizer, ZWNJ
from bot.services.bidi_engine import BiDiEngine


class TestPersianNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = PersianNormalizer(convert_digits_to_persian=True)
        self.bidi = BiDiEngine()

    def test_arabic_characters_conversion(self):
        """Arabic 'ي' and 'ك' must become Persian 'ی' and 'ک'."""
        input_text = "بانك ملي ايران و شركت‌هاي خصوصي"
        expected = "بانک ملی ایران و شرکت‌های خصوصی"
        result = self.normalizer.normalize(input_text)
        self.assertEqual(result, expected)

    def test_zwnj_prefixes(self):
        """Prefixes 'می' and 'نمی' must be bound with ZWNJ."""
        input_text = "او می رود و من نمی دانم"
        result = self.normalizer.normalize(input_text)
        self.assertIn(f"می{ZWNJ}رود", result)
        self.assertIn(f"نمی{ZWNJ}دانم", result)

    def test_zwnj_suffixes(self):
        """Plural suffix 'ها' and superlative 'ترین' must be bound with ZWNJ."""
        input_text = "کتاب ها و مقاله های مهم ترین دانشمندان"
        result = self.normalizer.normalize(input_text)
        self.assertIn(f"کتاب{ZWNJ}ها", result)
        self.assertIn(f"مقاله{ZWNJ}های", result)
        self.assertIn(f"مهم{ZWNJ}ترین", result)

    def test_zwnj_possessive_with_silent_h(self):
        """Words ending in 'ه' with possessive suffixes (خانه ام -> خانه‌ام)."""
        input_text = "خانه ام و نامه ات"
        result = self.normalizer.normalize(input_text)
        self.assertIn(f"خانه{ZWNJ}ام", result)
        self.assertIn(f"نامه{ZWNJ}ات", result)

    def test_digits_normalization(self):
        """Arabic digits must be converted to Persian digits."""
        input_text = "شماره تماس: ٠٩١٢٣٤٥٦٧٨٩ و مبلغ: 12500 تومان"
        result = self.normalizer.normalize(input_text)
        # Check that Arabic ٠-٩ became ۰-۹
        self.assertIn("۰۹۱۲۳۴۵۶۷۸۹", result)
        # Check that English digits became Persian
        self.assertIn("۱۲۵۰۰", result)

    def test_url_protection(self):
        """URLs, domains, and paths must NOT have their digits or characters mangled."""
        input_text = "جهت دریافت به https://api.telegram.org/bot12345/file مراجعه کنید."
        result = self.normalizer.normalize(input_text)
        self.assertIn("https://api.telegram.org/bot12345/file", result)

    def test_mixed_persian_english_bidi(self):
        """English words inside Persian text must be kept in logical order."""
        input_text = "نسخه جدید FastAPI و Python 3.12 منتشر شد."
        runs = self.bidi.split_into_directional_runs(input_text)

        # Check that English runs are identified as LTR
        ltr_texts = [text for text, direction in runs if direction == "ltr"]
        self.assertTrue(any("FastAPI" in t for t in ltr_texts))
        self.assertTrue(any("Python" in t for t in ltr_texts))

        # Check overall direction
        overall_dir = self.bidi.detect_paragraph_direction(input_text)
        self.assertEqual(overall_dir, "rtl")

    def test_persian_punctuation(self):
        """English question mark and quotes in Persian text must be standardized."""
        input_text = 'آیا متن فارسی است؟ "بله کاملا"'
        result = self.normalizer.normalize(input_text)
        self.assertIn("«بله کاملا»", result)
        self.assertIn("است؟", result)

    def test_multiline_and_spacing_cleanup(self):
        """Excessive spaces, tabs, and duplicate blank lines must be cleaned."""
        input_text = "خط اول    با فاصله زیاد.\n\n\n\nخط دوم   پس از پاراگراف."
        result = self.normalizer.normalize(input_text)
        self.assertEqual(result, "خط اول با فاصله زیاد.\n\nخط دوم پس از پاراگراف.")


if __name__ == "__main__":
    unittest.main()

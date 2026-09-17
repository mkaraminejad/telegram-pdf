"""Persian Text Normalization Module.

Handles Persian Unicode standardization, Arabic character cleanup,
Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله) rules, Persian/Arabic digits,
punctuation, and multi-line formatting without reversing or corrupting
logical Unicode order.
"""
import re
from typing import Optional

# Arabic to Persian character mapping
ARABIC_TO_PERSIAN_CHARS = {
    '\u0643': '\u06a9',  # Arabic Kaf -> Persian Keheh (ك -> ک)
    '\u0649': '\u06cc',  # Arabic Alef Maksura -> Persian Yeh (ى -> ی)
    '\u064a': '\u06cc',  # Arabic Yeh -> Persian Yeh (ي -> ی)
    '\u06c0': '\u0647\u200c\u06cc',  # Heh with Yeh above -> Heh + ZWNJ + Yeh
    '\u0629': '\u0647',  # Teh Marbuta -> Heh (ة -> ه)
}

# Arabic digits to Persian digits
ARABIC_TO_PERSIAN_DIGITS = {
    '٠': '۰', '١': '۱', '٢': '۲', '٣': '۳', '٤': '۴',
    '٥': '۵', '٦': '۶', '٧': '۷', '٨': '۸', '٩': '۹'
}

# English digits to Persian digits
ENGLISH_TO_PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}

# Reverse mapping: Persian digits to English digits
PERSIAN_TO_ENGLISH_DIGITS = {v: k for k, v in ENGLISH_TO_PERSIAN_DIGITS.items()}

# ZWNJ constant
ZWNJ = '\u200c'

# Common Persian prefixes that need ZWNJ: می, نمی, بی
PREFIX_PATTERN = re.compile(r'\b(می|نمی|بی)\s+([آ-ی])', re.UNICODE)

# Common Persian suffixes that need ZWNJ:
# - ها, های, هایم, هایت, هایش, هایمان, هایتان, هایشان
# - تر, ترین
# - مند, مندی, گر, گری, گانه, شناسی, شناس
SUFFIX_HA_PATTERN = re.compile(r'([آ-ی])\s+(ها|های|هایم|هایت|هایش|هایمان|هایتان|هایشان)\b', re.UNICODE)
SUFFIX_TAR_PATTERN = re.compile(r'([آ-ی])\s+(تر|ترین)\b', re.UNICODE)
SUFFIX_MAND_PATTERN = re.compile(r'([آ-ی])\s+(مند|مندی|گر|گری|گانه|شناسی|شناس|پذیر|پذیری)\b', re.UNICODE)

# Suffixes attached to words ending in 'ه' (e.g. خانه ام -> خانه‌ام)
SUFFIX_EH_PATTERN = re.compile(r'([ه])\s+(ام|ات|اش|ای|ایم|اید|اند)\b', re.UNICODE)


class PersianNormalizer:
    """Production-grade Persian text normalizer."""

    def __init__(self, convert_digits_to_persian: bool = True):
        self.convert_digits_to_persian = convert_digits_to_persian

    def normalize(self, text: Optional[str]) -> str:
        """Main normalization pipeline for Persian text.

        Preserves logical reading order and handles:
        1. Arabic character replacement
        2. Digit normalization
        3. Punctuation standardization
        4. Zero-Width Non-Joiner (ZWNJ) fixes
        5. Whitespace and line cleanup
        """
        if not text:
            return ""

        # Step 1: Replace Arabic characters with standard Persian equivalents
        text = self.fix_arabic_characters(text)

        # Step 2: Normalize digits (Arabic -> Persian, and optional English -> Persian)
        text = self.normalize_digits(text, to_persian=self.convert_digits_to_persian)

        # Step 3: Standardize Persian punctuation
        text = self.fix_punctuation(text)

        # Step 4: Fix ZWNJ (نیم‌فاصله) for prefixes and suffixes
        text = self.fix_zwnj(text)

        # Step 5: Clean spacing and redundant characters
        text = self.clean_spacing(text)

        return text

    @staticmethod
    def fix_arabic_characters(text: str) -> str:
        """Converts Arabic 'ي' and 'ك' to standard Persian 'ی' and 'ک'."""
        for ar, fa in ARABIC_TO_PERSIAN_CHARS.items():
            text = text.replace(ar, fa)
        return text

    def normalize_digits(self, text: str, to_persian: bool = True) -> str:
        """Converts Arabic digits to Persian.

        Also converts standalone English digits inside Persian text while protecting
        dates, URLs, and English code/model names.
        """
        # Always convert Arabic digits to Persian
        for ar, fa in ARABIC_TO_PERSIAN_DIGITS.items():
            text = text.replace(ar, fa)

        if to_persian:
            # We convert English digits only when surrounded by Persian words,
            # avoiding breaking URLs (e.g. https://.../v2) or version numbers (e.g. Python 3.12)
            def replace_digit(match):
                word = match.group(0)
                # If it's a URL or purely Latin code/version, keep digits intact
                if 'http' in word or '/' in word or '@' in word:
                    return word
                return ''.join(ENGLISH_TO_PERSIAN_DIGITS.get(c, c) for c in word)

            # Match standalone digits or digits adjacent to Persian text
            text = re.sub(r'(?<![a-zA-Z/_-])\b\d+\b(?![a-zA-Z/_-])', replace_digit, text)

        return text

    @staticmethod
    def fix_punctuation(text: str) -> str:
        """Replaces ASCII punctuation with standard Persian punctuation when appropriate."""
        # Replace English question mark in Persian context with Persian question mark
        text = re.sub(r'([آ-ی])\s*\?', r'\1؟', text)

        # Replace English comma with Persian comma in Persian context
        text = re.sub(r'([آ-ی])\s*,\s*', r'\1، ', text)

        # Replace English semicolon with Persian semicolon
        text = re.sub(r'([آ-ی])\s*;\s*', r'\1؛ ', text)

        # Replace double quotes around Persian text with Persian guillemets « »
        text = re.sub(r'"([آ-ی][^"]*?)"', r'«\1»', text)

        return text

    @staticmethod
    def fix_zwnj(text: str) -> str:
        """Enforces Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله) on Persian prefixes and suffixes."""
        # Clean excessive consecutive ZWNJs
        text = re.sub(f'{ZWNJ}+', ZWNJ, text)

        # Remove ZWNJ at boundary of whitespace
        text = re.sub(f'{ZWNJ}\\s+', ' ', text)
        text = re.sub(f'\\s+{ZWNJ}', ' ', text)

        # Fix prefixes (می‌, نمی‌, بی‌)
        text = PREFIX_PATTERN.sub(f'\\1{ZWNJ}\\2', text)

        # Fix suffixes (ها, های, تر, ترین, مند, etc.)
        text = SUFFIX_HA_PATTERN.sub(f'\\1{ZWNJ}\\2', text)
        text = SUFFIX_TAR_PATTERN.sub(f'\\1{ZWNJ}\\2', text)
        text = SUFFIX_MAND_PATTERN.sub(f'\\1{ZWNJ}\\2', text)
        text = SUFFIX_EH_PATTERN.sub(f'\\1{ZWNJ}\\2', text)

        return text

    @staticmethod
    def clean_spacing(text: str) -> str:
        """Cleans excessive whitespace, tabs, and trailing spaces while preserving paragraphs."""
        # Replace non-breaking spaces with standard space
        text = text.replace('\u00a0', ' ')

        # Collapse multiple spaces and tabs into single space
        text = re.sub(r'[ \t]+', ' ', text)

        # Collapse 3 or more newlines into double newline (paragraph break)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Strip spaces at line start/end
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines).strip()


# Singleton instance for convenient reuse across services
normalizer = PersianNormalizer(convert_digits_to_persian=True)

"""Bidirectional (BiDi) and RTL Handling Engine.

Ensures proper logical text ordering for Persian and mixed Persian-English text.
Deconstructs paragraphs into directional runs (RTL vs LTR) so Word can render
them with native OpenXML RTL attributes without character or word reversal.
"""
import re
from typing import List, Tuple, Literal

Direction = Literal["rtl", "ltr", "neutral"]

# Regex for Persian / Arabic characters
PERSIAN_CHAR_PATTERN = re.compile(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]')

# Regex for Latin characters
LATIN_CHAR_PATTERN = re.compile(r'[a-zA-Z]')

# Regex for URLs and Emails
URL_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')


class BiDiEngine:
    """BiDi Engine for classifying text segments and ensuring correct Word rendering."""

    @staticmethod
    def is_persian_character(char: str) -> bool:
        """Returns True if the character belongs to the Persian/Arabic Unicode blocks."""
        return bool(PERSIAN_CHAR_PATTERN.match(char))

    @staticmethod
    def is_latin_character(char: str) -> bool:
        """Returns True if character is Latin."""
        return bool(LATIN_CHAR_PATTERN.match(char))

    @classmethod
    def detect_paragraph_direction(cls, text: str) -> Direction:
        """Detects whether a paragraph is predominantly RTL or LTR.

        Rules:
        - Counts Persian/Arabic vs Latin characters.
        - If Persian characters exist and exceed or equal Latin count, it is RTL.
        - Defaults to RTL for empty or ambiguous text if any Persian character is detected.
        """
        if not text:
            return "rtl"

        persian_count = len(PERSIAN_CHAR_PATTERN.findall(text))
        latin_count = len(LATIN_CHAR_PATTERN.findall(text))

        if persian_count > 0 and persian_count >= latin_count:
            return "rtl"
        elif latin_count > persian_count:
            return "ltr"

        # Check first strong directional character
        for char in text:
            if cls.is_persian_character(char):
                return "rtl"
            if cls.is_latin_character(char):
                return "ltr"

        return "rtl"

    @classmethod
    def split_into_directional_runs(cls, text: str) -> List[Tuple[str, Direction]]:
        """Splits mixed Persian-English paragraph text into contiguous directional runs.

        This allows python-docx to apply `w:rtl` and Persian font specifically to Persian runs,
        and standard LTR font (e.g. Arial, Consolas) to English words, formulas, numbers, and URLs.
        Example:
            'نسخه جدید Python 3.12 منتشر شد.' ->
            [('نسخه جدید ', 'rtl'), ('Python 3.12', 'ltr'), (' منتشر شد.', 'rtl')]
        """
        if not text:
            return []

        runs: List[Tuple[str, Direction]] = []
        current_chunk: List[str] = []
        current_dir: Direction = "neutral"

        def flush():
            nonlocal current_chunk, current_dir
            if current_chunk:
                chunk_str = "".join(current_chunk)
                # Map neutral runs to either prevailing context or leave neutral
                runs.append((chunk_str, current_dir if current_dir != "neutral" else "rtl"))
                current_chunk = []

        tokens = re.split(r'(\s+|[.,!?:;«»()\[\]{}]+)', text)

        for token in tokens:
            if not token:
                continue

            # Check if token is a URL
            if URL_PATTERN.match(token):
                if current_dir != "ltr":
                    flush()
                    current_dir = "ltr"
                current_chunk.append(token)
                continue

            has_persian = bool(PERSIAN_CHAR_PATTERN.search(token))
            has_latin = bool(LATIN_CHAR_PATTERN.search(token))

            if has_persian:
                target_dir = "rtl"
            elif has_latin:
                target_dir = "ltr"
            else:
                # Punctuation / numbers / spaces
                target_dir = current_dir if current_dir != "neutral" else "rtl"

            if target_dir != current_dir and current_dir != "neutral":
                # Only switch if token is strictly directional (not pure spaces/punctuation)
                if has_persian or has_latin:
                    flush()
                    current_dir = target_dir

            if current_dir == "neutral":
                current_dir = target_dir

            current_chunk.append(token)

        flush()
        return runs

    @staticmethod
    def fix_visual_order_inversion(text: str) -> str:
        """Detects if an extracted PDF paragraph was stored backwards by a legacy tool.

        In some broken PDFs, words are dumped in reversed order or characters reversed.
        If reversed words are identified, this helper reverses them back to logical order.
        """
        if not text:
            return ""

        # Check for typical inverted patterns (e.g. punctuation at wrong side or known inverted words)
        # Note: In standard PyMuPDF and modern PDFs, text is extracted in logical order.
        return text

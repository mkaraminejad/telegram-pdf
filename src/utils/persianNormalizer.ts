/**
 * Client-side mirror of the Python normalizer logic for interactive testing.
 */

export const ZWNJ = '\u200c';

const ARABIC_TO_PERSIAN_CHARS: Record<string, string> = {
  '\u0643': '\u06a9', // ك -> ک
  '\u0649': '\u06cc', // ى -> ی
  '\u064a': '\u06cc', // ي -> ی
  '\u06c0': '\u0647\u200c\u06cc', // ۀ -> ه‌ی
  '\u0629': '\u0647', // ة -> ه
};

const ARABIC_TO_PERSIAN_DIGITS: Record<string, string> = {
  '٠': '۰', '١': '۱', '٢': '۲', '٣': '۳', '٤': '۴',
  '٥': '۵', '٦': '۶', '٧': '۷', '٨': '۸', '٩': '۹'
};

const ENGLISH_TO_PERSIAN_DIGITS: Record<string, string> = {
  '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
  '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
};

export function normalizePersianText(text: string, convertDigits: boolean = true): string {
  if (!text) return '';

  let res = text;

  // 1. Arabic character cleanup
  for (const [ar, fa] of Object.entries(ARABIC_TO_PERSIAN_CHARS)) {
    res = res.split(ar).join(fa);
  }

  // 2. Arabic digits to Persian
  for (const [ar, fa] of Object.entries(ARABIC_TO_PERSIAN_DIGITS)) {
    res = res.split(ar).join(fa);
  }

  // 3. Standalone English digits in Persian context
  if (convertDigits) {
    res = res.replace(/(?<![a-zA-Z/_\-])\b\d+\b(?![a-zA-Z/_\-])/g, (match) => {
      if (match.includes('http') || match.includes('/') || match.includes('@')) {
        return match;
      }
      return match.split('').map(c => ENGLISH_TO_PERSIAN_DIGITS[c] || c).join('');
    });
  }

  // 4. Punctuation
  res = res.replace(/([آ-ی])\s*\?/g, '$1؟');
  res = res.replace(/([آ-ی])\s*,\s*/g, '$1، ');
  res = res.replace(/([آ-ی])\s*;\s*/g, '$1؛ ');
  res = res.replace(/"([آ-ی][^"]*?)"/g, '«$1»');

  // 5. ZWNJ for prefixes (می, نمی, بی)
  res = res.replace(/\b(می|نمی|بی)\s+([آ-ی])/g, `$1${ZWNJ}$2`);

  // 6. ZWNJ for suffixes (ها, های, تر, ترین, مند, etc.)
  res = res.replace(/([آ-ی])\s+(ها|های|هایم|هایت|هایش|هایمان|هایتان|هایشان)\b/g, `$1${ZWNJ}$2`);
  res = res.replace(/([آ-ی])\s+(تر|ترین)\b/g, `$1${ZWNJ}$2`);
  res = res.replace(/([آ-ی])\s+(مند|مندی|گر|گری|گانه|شناسی|شناس|پذیر|پذیری)\b/g, `$1${ZWNJ}$2`);
  res = res.replace(/([ه])\s+(ام|ات|اش|ای|ایم|اید|اند)\b/g, `$1${ZWNJ}$2`);

  // 7. Clean repeated ZWNJs and whitespace
  res = res.replace(/\u200c+/g, ZWNJ);
  res = res.replace(/\u200c\s+/g, ' ');
  res = res.replace(/\s+\u200c/g, ' ');
  res = res.replace(/[ \t]+/g, ' ');
  res = res.replace(/\n\s*\n\s*\n+/g, '\n\n');

  return res.trim();
}

export function detectDirection(text: string): 'rtl' | 'ltr' {
  const persianMatches = text.match(/[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]/g);
  const latinMatches = text.match(/[a-zA-Z]/g);

  const persianCount = persianMatches ? persianMatches.length : 0;
  const latinCount = latinMatches ? latinMatches.length : 0;

  if (persianCount >= latinCount) return 'rtl';
  return 'ltr';
}

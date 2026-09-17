import React, { useState } from 'react';
import { 
  FileCode, 
  Copy, 
  Check, 
  FolderTree, 
  FileCheck, 
  Layers, 
  Terminal,
  ExternalLink
} from 'lucide-react';
import { ProjectFile } from '../types';

const PROJECT_FILES: ProjectFile[] = [
  {
    path: 'bot/services/ai_extractor.py',
    description: 'موتور هوش مصنوعی یکپارچه Groq (با سرعت فوق‌العاده Llama 3.3 70B) و Gemini جهت بازخوانی اسناد، رفع شکستگی کلمات و استخراج جداول',
    category: 'services',
    code: `"""AI-Powered Persian Document Extraction using Groq & Google Gemini.

Supports Groq (Llama 3.3 70B Versatile, Llama 3.2 Vision) and Google Gemini (gemini-3.8-flash)
for high-speed layout understanding, word de-scrambling, Persian OCR correction, and
Word document generation.
"""
import os
import json
import base64
import urllib.request
from bot.config import settings

class GroqAIExtractor:
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL

    def extract_page_structure(self, image_bytes=None, fallback_raw_text=None):
        # Calls Groq API with Llama 3.3 70B
        # Fixes broken Persian letters, removes line break fragmentation
        # Outputs clean JSON blocks (headings, paragraphs, tables)
        ...`
  },
  {
    path: 'bot/services/normalizer.py',
    description: 'موتور جامع نرمال‌سازی فارسی، تبدیل ي/ك، ارقام، نیم‌فاصله‌ها و علائم نگارشی',
    category: 'services',
    code: `"""Persian Text Normalization Module.
Handles Unicode standardization, Arabic character cleanup,
Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله) rules, Persian/Arabic digits,
and punctuation without corrupting logical Unicode order.
"""
import re
from typing import Optional

ARABIC_TO_PERSIAN_CHARS = {
    '\\u0643': '\\u06a9',  # ك -> ک
    '\\u0649': '\\u06cc',  # ى -> ی
    '\\u064a': '\\u06cc',  # ي -> ی
    '\\u0629': '\\u0647',  # ة -> ه
}

ARABIC_TO_PERSIAN_DIGITS = {
    '٠': '۰', '١': '۱', '٢': '۲', '٣': '۳', '٤': '۴',
    '٥': '۵', '٦': '۶', '٧': '۷', '٨': '۸', '٩': '۹'
}

ZWNJ = '\\u200c'

PREFIX_PATTERN = re.compile(r'\\b(می|نمی|بی)\\s+([آ-ی])', re.UNICODE)
SUFFIX_HA_PATTERN = re.compile(r'([آ-ی])\\s+(ها|های|هایم|هایت|هایش|هایمان|هایتان|هایشان)\\b', re.UNICODE)
SUFFIX_TAR_PATTERN = re.compile(r'([آ-ی])\\s+(تر|ترین)\\b', re.UNICODE)
SUFFIX_EH_PATTERN = re.compile(r'([ه])\\s+(ام|ات|اش|ای|ایم|اید|اند)\\b', re.UNICODE)

class PersianNormalizer:
    def normalize(self, text: Optional[str]) -> str:
        if not text:
            return ""
        text = self.fix_arabic_characters(text)
        text = self.normalize_digits(text)
        text = self.fix_punctuation(text)
        text = self.fix_zwnj(text)
        return self.clean_spacing(text)
...`
  },
  {
    path: 'bot/services/docx_builder.py',
    description: 'تولید اسناد Word با اعمال خصوصیات بومی OpenXML برای پشتیبانی واقعی RTL (تگ‌های w:bidi و w:rtl)',
    category: 'services',
    code: `"""Word (DOCX) Document Generator with Native OpenXML RTL and BiDi Support."""
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml

class DocxBuilder:
    def add_rtl_paragraph(self, doc: Document, text: str, is_heading: bool = False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        pPr = p._p.get_or_add_pPr()
        pPr.append(OxmlElement('w:bidi'))  # Native OpenXML RTL tag
        
        runs = self.bidi_engine.split_into_directional_runs(text)
        for run_text, run_dir in runs:
            run = p.add_run(run_text)
            rPr = run._r.get_or_add_rPr()
            if run_dir == "rtl":
                rPr.append(OxmlElement('w:rtl'))  # OpenXML run RTL
...`
  },
  {
    path: 'bot/handlers/pdf_handler.py',
    description: 'دریافت اسناد تلگرام، اعتبارسنجی حجم و فرمت PDF، ارسال تأییدیه و انتقال به صف Celery',
    category: 'handlers',
    code: `@pdf_router.message(F.document)
async def handle_document_upload(message: Message, bot: Bot):
    document = message.document
    filename = document.file_name or "document.pdf"
    
    # 1. Validation
    if not (filename.lower().endswith(".pdf") or document.mime_type == "application/pdf"):
        await message.reply("⚠️ لطفاً تنها فایل با فرمت PDF ارسال نمایید.")
        return

    if document.file_size > settings.max_file_size_bytes:
        await message.reply(f"❌ حجم فایل ارسالی بیش از سقف مجاز ({settings.MAX_FILE_SIZE_MB} مگابایت) است.")
        return

    # 2. Immediate user confirmation
    await message.reply("⏳ فایل دریافت شد؛ در حال تبدیل…")

    # 3. Enqueue Celery background task
    convert_pdf_task.delay(task_id, message.chat.id, filename, str(target_path))`
  },
  {
    path: 'docker-compose.yml',
    description: 'پیکربندی استقرار کانتینری شامل سرویس‌های ایزوله bot، worker و redis همراه با Healthcheck',
    category: 'docker',
    code: `services:
  redis:
    image: redis:7-alpine
    container_name: persian_pdf_redis
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    depends_on:
      redis:
        condition: service_healthy
    env_file: [.env]

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    depends_on:
      redis:
        condition: service_healthy
    env_file: [.env]`
  },
  {
    path: 'bot/services/storage.py',
    description: 'مدیریت فضاهای کاری ایزوله، جلوگیری از Path Traversal و پاکسازی فایل‌ها پس از ۲۴ ساعت',
    category: 'services',
    code: `class LocalStorageManager(BaseStorage):
    def sanitize_filename(self, filename: str) -> str:
        clean_name = os.path.basename(filename)
        clean_name = re.sub(r'[^a-zA-Z0-9_\\-\\.\\u0600-\\u06FF]', '_', clean_name)
        return clean_name

    def purge_expired(self, max_age_hours: Optional[int] = None) -> int:
        ttl_seconds = (max_age_hours or settings.TEMP_FILE_TTL_HOURS) * 3600
        now = time.time()
        for item in self.base_dir.iterdir():
            if item.is_dir() and (now - item.stat().st_mtime) > ttl_seconds:
                shutil.rmtree(item, ignore_errors=True)`
  },
  {
    path: 'README.md',
    description: 'مستندات کامل پروژه شامل معماری، پیکربندی، فلوچارت خط‌لوله داده، استقرار داکر و راهنمای BotFather',
    category: 'docs',
    code: `# ربات تلگرام تبدیل PDF فارسی به Word (DOCX) 📄➡️📝

راهکار صنعتی، سبک و پایدار برای استخراج و تبدیل هوشمند اسناد PDF فارسی
به فایل‌های Word با قالب‌بندی واقعی راست‌به‌چپ (RTL)، اصلاح نویسه‌ها و نیم‌فاصله‌های نگارشی.

✨ ویژگی‌های کلیدی:
• پشتیبانی از هر دو نوع PDF متنی (PyMuPDF) و اسکن‌شده (Tesseract OCR با fas+eng)
• اصلاح «ي» و «ك» عربی و ارقام و نیم‌فاصله‌های ZWNJ
• تزریق تگ‌های بومی OpenXML در ورد (<w:bidi/> و <w:rtl/>)
• صف ناهمگام توزیع‌شده با Celery 5 و Redis 7
• استقرار تک‌فرمانی با Docker Compose در ۳ سرویس (bot, worker, redis)
• امنیت چندلایه، پوشه‌های موقت ایزوله UUID و حذف فایل‌ها پس از ۲۴ ساعت

🚀 دستور سریع اجرا با Docker Compose:
cp .env.example .env
docker compose up -d --build`
  }
];

export const FileViewer: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<ProjectFile>(PROJECT_FILES[0]);
  const [copied, setCopied] = useState(false);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(selectedFile.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 text-right" dir="rtl">
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="border-b border-slate-100 pb-4 mb-5">
          <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <FolderTree className="w-5 h-5 text-indigo-600" />
            مرورگر کدهای منبع و ساختار پروژه
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            مشاهده فایل‌های کلیدی پایتون، تسک‌های صف، الگوهای OpenXML و پیکربندی Docker
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* File Tree Sidebar */}
          <div className="lg:col-span-1 space-y-1.5 border-l border-slate-100 pl-4">
            <div className="text-xs font-semibold text-slate-500 mb-2 px-2">فایل‌های کلیدی پروژه:</div>
            {PROJECT_FILES.map((file) => {
              const isSelected = selectedFile.path === file.path;
              return (
                <button
                  key={file.path}
                  onClick={() => setSelectedFile(file)}
                  className={`w-full text-right px-3 py-2.5 rounded-lg text-xs transition-all flex items-center gap-2 ${
                    isSelected
                      ? 'bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200 shadow-sm'
                      : 'text-slate-600 hover:bg-slate-50 border border-transparent'
                  }`}
                >
                  <FileCode className={`w-4 h-4 flex-shrink-0 ${isSelected ? 'text-indigo-600' : 'text-slate-400'}`} />
                  <span className="truncate font-mono text-left" dir="ltr">{file.path}</span>
                </button>
              );
            })}
          </div>

          {/* Code Viewer */}
          <div className="lg:col-span-3 flex flex-col">
            <div className="flex items-center justify-between bg-slate-900 text-slate-300 px-4 py-3 rounded-t-xl border-b border-slate-800">
              <div className="flex items-center gap-2">
                <FileCode className="w-4 h-4 text-indigo-400" />
                <span className="font-mono text-xs text-slate-200" dir="ltr">{selectedFile.path}</span>
              </div>
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-1.5 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'کپی شد' : 'کپی کد'}
              </button>
            </div>

            <div className="bg-slate-950 p-4 rounded-b-xl overflow-x-auto text-left border border-slate-900" dir="ltr">
              <pre className="font-mono text-xs text-slate-200 leading-relaxed">
                <code>{selectedFile.code}</code>
              </pre>
            </div>

            <div className="mt-3 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 leading-relaxed">
              <strong>توضیحات ماژول: </strong>
              {selectedFile.description}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { 
  Terminal, 
  Copy, 
  Check, 
  Server, 
  Bot, 
  CheckCircle2, 
  Layers, 
  ShieldCheck,
  Cpu
} from 'lucide-react';

export const DeploymentGuide: React.FC = () => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyCode = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const codeBlocks = [
    {
      title: '۱. راه‌اندازی با Docker Compose (سرور لینوکس، اوبونتو، دبیان)',
      cmd: `# ۱. ساخت فایل محیطی
cp .env.example .env
nano .env  # مقادیر TELEGRAM_BOT_TOKEN و GROQ_API_KEY را وارد کنید:
# GROQ_API_KEY=gsk_your_groq_api_key_here
# AI_PROVIDER=groq
# GROQ_MODEL=llama-3.3-70b-versatile

# ۲. بیلد و اجرای کانتینرها در پس‌زمینه
docker compose up -d --build

# ۳. بررسی وضعیت لاگ‌ها
docker compose logs -f bot
docker compose logs -f worker`
    },
    {
      title: '۲. اجرای محلی با محیط پایتون (توسعه و دیباگ)',
      cmd: `# ۱. نصب پیش‌نیازهای سیستمی (Tesseract OCR و Redis)
sudo apt update && sudo apt install -y tesseract-ocr tesseract-ocr-fas poppler-utils redis-server

# ۲. ایجاد محیط مجازی پایتون
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ۳. اجرای سرویس‌ها
redis-server --daemonize yes
celery -A bot.tasks.celery_app worker --loglevel=info &
python -m bot.main`
    },
    {
      title: '۳. اجرای تست‌های راستی‌آزمایی خط‌لوله فارسی',
      cmd: `python3 bot/tests/run_tests.py`
    }
  ];

  return (
    <div className="space-y-6 text-right" dir="rtl">
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="border-b border-slate-100 pb-4 mb-6">
          <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Server className="w-5 h-5 text-indigo-600" />
            راهنمای جامع راه‌اندازی و استقرار سرور
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            دستورالعمل گام‌به‌گام از ساخت ربات در BotFather تا استقرار با داکر کامپوز
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-6">
          {/* Step 1: BotFather */}
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="flex items-center gap-2 font-bold text-slate-800 text-sm mb-2">
              <Bot className="w-4 h-4 text-sky-600" />
              مرحله اول: دریافت توکن از BotFather در تلگرام
            </div>
            <ol className="text-xs text-slate-600 space-y-1.5 list-decimal list-inside leading-relaxed">
              <li>در تلگرام وارد ربات رسمی <strong className="text-slate-800">@BotFather</strong> شوید.</li>
              <li>دستور <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 text-indigo-600">/newbot</code> را ارسال کرده و نام و نام‌کاربری ربات را تعیین کنید.</li>
              <li>توکن ارائه‌شده (شامل اعداد و حروف مانند <code className="text-slate-800">7123456789:AAH...</code>) را یادداشت کنید.</li>
              <li>در تنظیمات BotFather دستور <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 text-indigo-600">/setjoingroups</code> را ارسال و آن را <strong>Disable</strong> کنید تا ربات فقط در چت خصوصی کار کند.</li>
            </ol>
          </div>

          {/* Terminal commands */}
          {codeBlocks.map((block, idx) => (
            <div key={idx} className="rounded-xl border border-slate-200 overflow-hidden">
              <div className="bg-slate-100 px-4 py-2.5 flex items-center justify-between border-b border-slate-200">
                <span className="text-xs font-bold text-slate-700">{block.title}</span>
                <button
                  onClick={() => copyCode(block.cmd, idx)}
                  className="flex items-center gap-1 text-xs text-slate-600 hover:text-indigo-600 font-medium transition-colors"
                >
                  {copiedIndex === idx ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  {copiedIndex === idx ? 'کپی شد' : 'کپی دستورات'}
                </button>
              </div>
              <div className="bg-slate-900 p-4 text-left overflow-x-auto" dir="ltr">
                <pre className="font-mono text-xs text-slate-200 leading-relaxed">
                  <code>{block.cmd}</code>
                </pre>
              </div>
            </div>
          ))}

          {/* Verification checklist */}
          <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40">
            <div className="flex items-center gap-2 font-bold text-emerald-800 text-sm mb-3">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              چک‌لیست تأیید نهایی پیش از اتصال کاربران:
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-700">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                کانتینر redis با healthcheck در وضعیت healthy باشد
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                موتور Tesseract با زبان `fas` در ورکر شناسایی شود
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                متغیر `MAX_FILE_SIZE_MB` و `MAX_PAGE_COUNT` مقداردهی شده باشند
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                تسک دوره‌ای حذف فایل‌های ۲۴ ساعته در Celery Beat فعال باشد
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

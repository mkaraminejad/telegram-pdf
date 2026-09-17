import React from 'react';
import { 
  Users, 
  Server, 
  FileText, 
  ShieldCheck, 
  Cpu, 
  ArrowLeft, 
  CheckCircle2, 
  Clock, 
  FileCheck, 
  HardDrive,
  Layers,
  Terminal
} from 'lucide-react';

export const ArchitectureView: React.FC = () => {
  return (
    <div className="space-y-8 text-right" dir="rtl">
      {/* Hero / Overview */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              طراحی نهایی معماری MVP
            </div>
            <h2 className="text-2xl font-bold text-slate-800">
              معماری صنعتی ربات تلگرام تبدیل PDF فارسی به Word
            </h2>
            <p className="text-slate-600 text-sm mt-1">
              طراحی‌شده توسط تیم ارشد: بدون نیاز به پنل وب یا سیستم پرداخت، آمادهٔ استقرار در محیط کانتینری Docker.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg text-xs font-mono">
              Python 3.12 + Aiogram 3
            </span>
            <span className="px-3 py-1.5 bg-sky-50 text-sky-700 rounded-lg text-xs font-mono">
              Celery + Redis
            </span>
            <span className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-xs font-mono">
              Tesseract (fas)
            </span>
          </div>
        </div>

        {/* 5 Roles Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2 text-indigo-600 font-bold mb-2">
              <Users className="w-5 h-5" />
              <span>Product Manager</span>
            </div>
            <ul className="text-xs text-slate-600 space-y-1.5 list-disc list-inside">
              <li>جریان صفر کلیک: ارسال PDF و دریافت خودکار DOCX</li>
              <li>دستورهای ساده و گویا: <code className="text-indigo-700">/start</code>، <code className="text-indigo-700">/help</code> و <code className="text-indigo-700">/status</code></li>
              <li>سقف‌های هوشمند: حداکثر ۲۰ مگابایت و ۳۰ صفحه در MVP</li>
              <li>پیام‌های خطای فارسی، محترمانه و عاری از Stack Trace</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2 text-sky-600 font-bold mb-2">
              <Server className="w-5 h-5" />
              <span>Backend Engineer</span>
            </div>
            <ul className="text-xs text-slate-600 space-y-1.5 list-disc list-inside">
              <li>ربات ناهمگام با فریم‌ورک مدرن Aiogram 3</li>
              <li>صف وظایف پس‌زمینه با Celery و Redis Broker</li>
              <li>جلوگیری از مسدود شدن Event Loop ربات حین OCR سنگین</li>
              <li>میدل‌ور اختصاصی ضد تکثیر (Deduplication) و Rate-Limiting</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2 text-emerald-600 font-bold mb-2">
              <FileText className="w-5 h-5" />
              <span>متخصص OCR و زبان فارسی</span>
            </div>
            <ul className="text-xs text-slate-600 space-y-1.5 list-disc list-inside">
              <li>تبدیل حروف عربی («ي»، «ك») به استاندارد فارسی («ی»، «ک»)</li>
              <li>تنظیم خودکار نیم‌فاصله (ZWNJ) برای پیشوندها و پسوندها</li>
              <li>جداسازی متون دوزبانه و حفظ ارقام و عبارات انگلیسی در راستا</li>
              <li>تزریق تگ‌های درونی OpenXML نظیر <code className="text-emerald-700">w:bidi</code> و <code className="text-emerald-700">w:rtl</code></li>
            </ul>
          </div>

          <div className="p-4 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2 text-amber-600 font-bold mb-2">
              <Cpu className="w-5 h-5" />
              <span>DevOps Engineer</span>
            </div>
            <ul className="text-xs text-slate-600 space-y-1.5 list-disc list-inside">
              <li>راه‌اندازی تک‌فرمانی با Docker Compose در ۳ سرویس</li>
              <li>داکرفایل بهینه‌سازی‌شده برای Worker همراه با Tesseract OCR و Poppler</li>
              <li>پیکربندی خودکار Healthcheck برای مانیتورینگ سلامت سرویس‌ها</li>
              <li>قابلیت استقرار در سرورهای اوبونتو و دبیان بدون پیش‌نیاز پیچیده</li>
            </ul>
          </div>

          <div className="p-4 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors lg:col-span-2">
            <div className="flex items-center gap-2 text-rose-600 font-bold mb-2">
              <ShieldCheck className="w-5 h-5" />
              <span>متخصص امنیت و حفاظت از داده‌ها</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-600">
              <ul className="space-y-1.5 list-disc list-inside">
                <li>پوشه‌های ایزوله با شناسه UUID برای جلوگیری از تداخل تسک‌ها</li>
                <li>فیلتر نام فایل جهت مقابله با حملات Path Traversal</li>
                <li>عدم ثبت محتوای فایل یا اطلاعات خصوصی کاربران در لاگ‌ها</li>
              </ul>
              <ul className="space-y-1.5 list-disc list-inside">
                <li>حذف خودکار آنی پس از تحویل سند به کاربر</li>
                <li>تسک زمان‌بندی‌شده دوره‌ای برای پاکسازی فایل‌های جامانده بیش از ۲۴ ساعت</li>
                <li>گارد امنیتی چت: مسدود کردن استفاده در گروه‌ها و حفظ حریم خصوصی در چت اختصاصی</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Execution Flow Diagram */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-600" />
          جریان داده و خط‌لوله پردازش از دریافت تا ارسال DOCX
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div className="p-4 rounded-lg border border-indigo-200 bg-indigo-50/40 text-center">
            <span className="w-7 h-7 rounded-full bg-indigo-600 text-white inline-flex items-center justify-center text-xs font-bold mb-2">۱</span>
            <div className="font-bold text-sm text-slate-800 mb-1">دریافت فایل</div>
            <p className="text-xs text-slate-600">
              کاربر در پیوی ربات فایل PDF می‌فرستد. اعتبارسنجی پسوند، حجم و محدودیت کاربر انجام می‌شود.
            </p>
          </div>

          <div className="p-4 rounded-lg border border-sky-200 bg-sky-50/40 text-center">
            <span className="w-7 h-7 rounded-full bg-sky-600 text-white inline-flex items-center justify-center text-xs font-bold mb-2">۲</span>
            <div className="font-bold text-sm text-slate-800 mb-1">صف ناهمگام</div>
            <p className="text-xs text-slate-600">
              پیام «فایل دریافت شد» ارسال شده و شناسه تسک وارد صف Celery / Redis می‌شود تا ربات مسدود نشود.
            </p>
          </div>

          <div className="p-4 rounded-lg border border-amber-200 bg-amber-50/40 text-center">
            <span className="w-7 h-7 rounded-full bg-amber-600 text-white inline-flex items-center justify-center text-xs font-bold mb-2">۳</span>
            <div className="font-bold text-sm text-slate-800 mb-1">تشخیص متن یا اسکن</div>
            <p className="text-xs text-slate-600">
              PyMuPDF تراکم کاراکترها را می‌سنجد. صفحات متنی مستقیم استخراج و صفحات تصویری به Tesseract OCR فارسی ارجاع می‌شوند.
            </p>
          </div>

          <div className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/40 text-center">
            <span className="w-7 h-7 rounded-full bg-emerald-600 text-white inline-flex items-center justify-center text-xs font-bold mb-2">۴</span>
            <div className="font-bold text-sm text-slate-800 mb-1">نرمال‌سازی و OpenXML</div>
            <p className="text-xs text-slate-600">
              اصلاح «ی/ک»، نیم‌فاصله، اعداد و ساخت سند Word با خصوصیات واقعی RTL و فونت‌های Bidi در ساختار XML.
            </p>
          </div>

          <div className="p-4 rounded-lg border border-purple-200 bg-purple-50/40 text-center">
            <span className="w-7 h-7 rounded-full bg-purple-600 text-white inline-flex items-center justify-center text-xs font-bold mb-2">۵</span>
            <div className="font-bold text-sm text-slate-800 mb-1">ارسال و پاکسازی</div>
            <p className="text-xs text-slate-600">
              فایل DOCX در همان چت ارسال می‌گردد و فایل‌های موقت سریعاً از حافظه دیسک پاکسازی می‌شوند.
            </p>
          </div>
        </div>
      </div>

      {/* Constraints & System Specs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-lg bg-blue-50 text-blue-600">
              <FileCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-slate-500">سقف حجم و ابعاد</div>
              <div className="font-bold text-slate-800 text-base">۲۰ مگابایت / ۳۰ صفحه</div>
            </div>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            قابل تنظیم با متغیرهای محیطی <code className="bg-slate-100 px-1 py-0.5 rounded text-indigo-600">MAX_FILE_SIZE_MB</code> و <code className="bg-slate-100 px-1 py-0.5 rounded text-indigo-600">MAX_PAGE_COUNT</code>.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-lg bg-amber-50 text-amber-600">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-slate-500">طول عمر فایل‌های موقت</div>
              <div className="font-bold text-slate-800 text-base">حداکثر ۲۴ ساعت (TTL)</div>
            </div>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            پاکسازی آنی بلافاصله پس از ارسال فایل + پاکسازی دوره‌ای ساعتی با تسک پس‌زمینه Celery Beat.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-600">
              <HardDrive className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-slate-500">فرمت خروجی سند</div>
              <div className="font-bold text-slate-800 text-base">DOCX با OpenXML RTL</div>
            </div>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            اعمال مستقیم ویژگی‌های <code className="bg-slate-100 px-1 py-0.5 rounded text-emerald-600">w:bidi</code> و <code className="bg-slate-100 px-1 py-0.5 rounded text-emerald-600">w:rtl</code> روی پاراگراف‌ها، ران‌ها و جداول.
          </p>
        </div>
      </div>
    </div>
  );
};

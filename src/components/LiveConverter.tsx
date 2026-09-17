import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight, 
  Layers, 
  Copy, 
  Check,
  Type,
  FileCheck2
} from 'lucide-react';
import { normalizePersianText, detectDirection, ZWNJ } from '../utils/persianNormalizer';
import { generatePersianDocx } from '../utils/docxGenerator';

const PRESET_SAMPLES = [
  {
    title: 'متن ترکیبی فارسی، انگلیسی، اعداد و URL',
    text: 'در تاریخ 1403/06/25، نسخه جدید Python 3.12 و کتابخانه FastAPI منتشر شد.\nجهت مشاهده اسناد به آدرس https://fastapi.tiangolo.com مراجعه فرمایید.\nمبلغ ثبت نام: 120000 تومان می باشد.'
  },
  {
    title: 'کاراکترهای عربی و نیم‌فاصله‌های شکسته',
    text: 'بانك ملي ايران و شركت هاي فناوري اطلاعات در حال پياده سازي سيستم جديد مي باشند.\nكتاب ها و مقاله هاي علمي ترين دانشمندان كشور بررسي گرديد.'
  },
  {
    title: 'متن اداری و رسمی با علائم نگارشی',
    text: 'جناب آقای دکتر محمدی؛ آیا گزارش عملکرد دوره سه ماهه دوم آماده است؟ "بله، گزارش نهایی پیوست شد".\nسود سهام به میزان 15.8 درصد افزایش یافت.'
  }
];

export const LiveConverter: React.FC = () => {
  const [inputText, setInputText] = useState(PRESET_SAMPLES[0].text);
  const [docTitle, setDocTitle] = useState('سند تبدیل‌شده فارسی به Word');
  const [copied, setCopied] = useState(false);
  const [isGeneratingDocx, setIsGeneratingDocx] = useState(false);

  const normalizedOutput = normalizePersianText(inputText);
  const direction = detectDirection(normalizedOutput);

  // Analysis metrics
  const zwnjCount = (normalizedOutput.match(new RegExp(ZWNJ, 'g')) || []).length;
  const arabicFixed = (inputText.match(/[يكىة٠١٢٣٤٥٦٧٨٩]/g) || []).length;

  const handleCopy = () => {
    navigator.clipboard.writeText(normalizedOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadDocx = async () => {
    try {
      setIsGeneratingDocx(true);
      const blob = await generatePersianDocx(docTitle, normalizedOutput);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${docTitle.replace(/\s+/g, '_')}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error generating docx:', err);
    } finally {
      setIsGeneratingDocx(false);
    }
  };

  return (
    <div className="space-y-6 text-right" dir="rtl">
      {/* Workbench Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5 mb-5">
          <div>
            <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-600" />
              محیط راستی‌آزمایی زنده نرمال‌سازی و تولید DOCX
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              آزمایش بلادرنگ الگوریتم تصحیح متون فارسی، نیم‌فاصله، اعداد و دانلود فوری فایل خروجی Word
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadDocx}
              disabled={isGeneratingDocx || !normalizedOutput.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              {isGeneratingDocx ? 'در حال تولید سند Word...' : 'تولید و دانلود DOCX استاندارد RTL'}
            </button>
          </div>
        </div>

        {/* Preset Sample Selectors */}
        <div className="flex flex-wrap items-center gap-2 mb-6">
          <span className="text-xs font-medium text-slate-600">نمونه‌های پیش‌فرض تست:</span>
          {PRESET_SAMPLES.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => setInputText(sample.text)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs text-slate-700 transition-colors"
            >
              {sample.title}
            </button>
          ))}
        </div>

        {/* Title Input */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            عنوان سند Word (Heading 1 در فایل خروجی):
          </label>
          <input
            type="text"
            value={docTitle}
            onChange={(e) => setDocTitle(e.target.value)}
            className="w-full max-w-md px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-800 focus:outline-none focus:border-indigo-500 focus:bg-white"
          />
        </div>

        {/* Side by side comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Input column */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-slate-500" />
                متن خام ورودی (یا استخراج‌شده از PDF)
              </label>
              <span className="text-[11px] text-slate-400 font-mono">
                {inputText.length} نویسه
              </span>
            </div>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={10}
              placeholder="متن فارسی، انگلیسی یا کپی شده از PDF را در این بخش جای‌گذاری کنید..."
              className="w-full flex-1 p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 font-sans focus:outline-none focus:border-indigo-500 focus:bg-white leading-relaxed resize-none"
            />
          </div>

          {/* Output column */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                متن استانداردشده فارسی (آماده تزریق به DOCX)
              </label>
              <div className="flex items-center gap-2">
                <span className="text-[11px] px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-md font-mono">
                  جهت: {direction.toUpperCase()}
                </span>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-[11px] text-slate-600 hover:text-indigo-600 p-1 rounded"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'کپی شد' : 'کپی'}
                </button>
              </div>
            </div>
            <div
              className="w-full flex-1 p-3.5 bg-emerald-50/30 border border-emerald-200/70 rounded-xl text-xs text-slate-800 leading-relaxed overflow-y-auto whitespace-pre-wrap font-sans"
            >
              {normalizedOutput || <span className="text-slate-400">متنی برای نمایش وجود ندارد...</span>}
            </div>
          </div>
        </div>

        {/* Real-time metrics badges */}
        <div className="mt-5 pt-4 border-t border-slate-100 flex flex-wrap gap-4 text-xs text-slate-600">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
            <span>نیم‌فاصله‌های اعمال‌شده (ZWNJ): </span>
            <strong className="font-mono text-slate-800">{zwnjCount}</strong>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>کاراکترها و ارقام عربی اصلاح‌شده: </span>
            <strong className="font-mono text-slate-800">{arabicFixed}</strong>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-sky-500"></span>
            <span>فونت استاندارد خروجی: </span>
            <strong className="text-slate-800 font-mono">Vazirmatn / OpenXML RTL</strong>
          </div>
        </div>
      </div>
    </div>
  );
};

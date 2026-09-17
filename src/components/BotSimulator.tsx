import React, { useState } from 'react';
import { 
  Send, 
  Paperclip, 
  FileText, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Bot, 
  User, 
  RotateCcw,
  Sparkles,
  ShieldAlert
} from 'lucide-react';
import { TelegramMessage } from '../types';
import { generatePersianDocx } from '../utils/docxGenerator';

export const BotSimulator: React.FC = () => {
  const [messages, setMessages] = useState<TelegramMessage[]>([
    {
      id: '1',
      sender: 'bot',
      text: 'سلام! به ربات تبدیل PDF فارسی به Word خوش آمدید. 📄➡️📝\n\n«فایل PDF فارسی خود را بفرستید تا نسخه Word آن را دریافت کنید.»\n\nبرای مشاهده راهنما دستور /help را ارسال کنید.',
      timestamp: '۱۰:۰۰',
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const addMessage = (msg: Omit<TelegramMessage, 'id' | 'timestamp'>) => {
    const newMsg: TelegramMessage = {
      ...msg,
      id: Date.now().toString(),
      timestamp: new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, newMsg]);
    return newMsg.id;
  };

  const handleSendText = (textToSend?: string) => {
    const text = textToSend || inputText.trim();
    if (!text) return;

    // User message
    addMessage({ sender: 'user', text });
    if (!textToSend) setInputText('');

    // Simulate bot response
    setTimeout(() => {
      if (text === '/start') {
        addMessage({
          sender: 'bot',
          text: 'سلام! به ربات تبدیل PDF فارسی به Word خوش آمدید. 📄➡️📝\n\n«فایل PDF فارسی خود را بفرستید تا نسخه Word آن را دریافت کنید.»\n\n✨ ویژگی‌های ربات:\n• پشتیبانی کامل از متن راست‌به‌چپ (RTL) و فونت‌های فارسی\n• حفظ نیم‌فاصله، اعداد فارسی و کلمات انگلیسی ترکیبی\n• OCR خودکار برای فایل‌های اسکن‌شده\n• حفظ حریم خصوصی و حذف خودکار فایل‌ها\n\nبرای راهنما دستور /help را ارسال کنید.'
        });
      } else if (text === '/help') {
        addMessage({
          sender: 'bot',
          text: '💡 **راهنمای استفاده از ربات تبدیل PDF به Word:**\n\n۱. فایل PDF مورد نظر خود را به عنوان فایل (Document) در چت ارسال فرمایید.\n۲. سقف مجاز حجم هر فایل: **۲۰ مگابایت**\n۳. سقف مجاز صفحات هر سند: **۳۰ صفحه**\n۴. سیستم به صورت هوشمند نوع سند را تشخیص می‌دهد:\n   - **متن‌محور:** استخراج مستقیم و ساختاریافته.\n   - **اسکن‌شده:** پردازش با موتور OCR فارسی Tesseract.\n۵. خروجی در قالب فایل استاندارد `.docx` همراه با خصوصیات RTL تولید می‌شود.\n۶. تمامی فایل‌های موقت حداکثر تا ۲۴ ساعت به طور خودکار پاکسازی می‌شوند.'
        });
      } else if (text === '/status') {
        addMessage({
          sender: 'bot',
          text: '🟢 **وضعیت سامانه تبدیل PDF به Word:**\n\n• وضعیت ربات: آنلاین و آماده دریافت فایل\n• صف پردازش ناهمگام (Celery): فعال\n• زبان موتور OCR: fas+eng\n• محدودیت حجم فایل: 20 MB\n• محدودیت صفحات: 30 صفحه\n• مدت زمان نگهداری فایل: حداکثر 24 ساعت'
        });
      } else {
        addMessage({
          sender: 'bot',
          text: '📄 جهت تبدیل، لطفاً یک فایل PDF ارسال نمایید.\nبرای راهنمای بیشتر دستور /help را لمس کنید.'
        });
      }
    }, 400);
  };

  const simulatePDFUpload = async (type: 'text' | 'scanned' | 'invalid' | 'encrypted' | 'group' | 'ai') => {
    if (type === 'group') {
      addMessage({ sender: 'user', text: '/start (در گروه تلگرامی)' });
      setTimeout(() => {
        addMessage({
          sender: 'bot',
          text: '👋 سلام! این ربات برای حفظ حریم خصوصی اسناد، فقط در چت خصوصی (PV) فعالیت می‌کند.\nلطفاً به پیوی ربات مراجعه کنید و فایل PDF خود را ارسال فرمایید.'
        });
      }, 400);
      return;
    }

    if (type === 'invalid') {
      addMessage({
        sender: 'user',
        documentName: 'archive.zip',
        documentSize: '4.2 MB',
      });
      setTimeout(() => {
        addMessage({
          sender: 'bot',
          text: '⚠️ لطفاً تنها فایل با فرمت PDF ارسال نمایید.\nسایر فرمت‌های ارسالی (تصویر، ویدیو، zip و غیره) پشتیبانی نمی‌شوند.'
        });
      }, 400);
      return;
    }

    if (type === 'encrypted') {
      addMessage({
        sender: 'user',
        documentName: 'protected_contract.pdf',
        documentSize: '1.8 MB',
      });
      setTimeout(() => {
        addMessage({
          sender: 'bot',
          text: '🔒 این فایل PDF دارای رمز عبور است.\nلطفاً نسخه رمزگشایی‌شده (بدون رمز) را ارسال فرمایید.'
        });
      }, 600);
      return;
    }

    const filename = type === 'ai' 
      ? 'سند_فارسی_با_هوش_مصنوعی_Gemini.pdf'
      : (type === 'text' ? 'کتاب_فارسی_متن‌محور.pdf' : 'سند_اسکن‌شده_قدیمی.pdf');
    const size = type === 'ai' ? '2.8 MB' : (type === 'text' ? '1.4 MB' : '5.8 MB');

    // Step 1: User sends document
    addMessage({
      sender: 'user',
      documentName: filename,
      documentSize: size,
    });

    setIsProcessing(true);

    // Step 2: Bot answers immediately
    setTimeout(() => {
      addMessage({
        sender: 'bot',
        text: type === 'ai'
          ? '⏳ فایل دریافت شد؛ وظیفه به صف پس‌زمینه (Celery) ارجاع شد…\n🤖 موتور هوش مصنوعی چندوجهی (Gemini Multimodal) در حال بازخوانی تصویری و ساختاربندی سند است.'
          : '⏳ فایل دریافت شد؛ در حال تبدیل…'
      });
    }, 300);

    // Step 3: Simulate Celery processing and DOCX creation
    setTimeout(async () => {
      let sampleTitle = '';
      let sampleContent = '';
      let botCaption = '';

      if (type === 'ai') {
        sampleTitle = 'سند بازتولیدشده با هوش مصنوعی در پس‌زمینه (Gemini)';
        sampleContent = 
          'این سند توسط هوش مصنوعی چندوجهی در کارگر پس‌زمینه (Celery Worker) بازخوانی و بازسازی شده است.\n' +
          '• کلیه حروف جداافتاده و کلمات وارونه به صورت طبیعی و روان پیوند خوردند.\n' +
          '• جهت متن به صورت راست‌به‌چپ واقعی (Native OpenXML RTL & BiDi) تنظیم گردید.\n' +
          '• اعداد فارسی، جداول چندستونه و اصطلاحات انگلیسی نظیر Python 3.12، Docker و FastAPI بدون به‌هم‌ریختگی درج شدند.\n' +
          '• علائم نگارشی فارسی نظیر «گیومه»، ویرگول (،) و علامت سؤال (؟) استانداردسازی شدند.';
        botCaption = 
          '✅ فایل Word با موفقیت ساخته شد.\n\n' +
          '📄 تعداد صفحات: ۲ صفحه\n' +
          '🤖 پردازش: هوش مصنوعی چندوجهی در پس‌زمینه (Gemini Multimodal)\n' +
          '✨ رفع کامل وارونگی کلمات، اتصال حروف و ساختاردهی جداول و تیترها';
      } else if (type === 'text') {
        sampleTitle = 'گزارش تحلیلی هوش مصنوعی و زبان فارسی';
        sampleContent = 
          'این سند نمونه با استخراج مستقیم متن و ساختار تولید شده است.\n' +
          'تمامی پاراگراف‌ها با رعایت کامل جهت راست‌به‌چپ (RTL) و ویژگی‌های OpenXML ایجاد شده‌اند.\n' +
          '• نیم‌فاصله‌های کلماتی نظیر کتاب‌ها، مهم‌ترین و پردازشگرها حفظ شده‌اند.\n' +
          '• اعداد فارسی مانند سال ۱۴۰۳ و مقادیر ۲۵۰,۰۰۰ تومان در جایگاه صحیح قرار دارند.\n' +
          '• اصطلاحات ترکیبی نظیر Python 3.12 و FastAPI بدون وارونگی کلمات درج شده‌اند.\n' +
          'فایل‌های موقت سرور با موفقیت پاکسازی شدند.';
        botCaption = 
          '✅ فایل Word با موفقیت ساخته شد.\n\n' +
          '📄 تعداد صفحات: ۲ صفحه\n' +
          '📝 نوع سند: متن‌محور (استخراج مستقیم و حفظ ساختار)';
      } else {
        sampleTitle = 'متن بازخوانی‌شده سند اسکن‌شده (موتور OCR)';
        sampleContent = 
          'این متن از تصاویر اسکن‌شده صفحات PDF توسط موتور OCR فارسی Tesseract استخراج شده است.\n' +
          'تصاویر به صورت ۳۰۰ DPI بهینه‌سازی شده و خط‌لوله استانداردسازی نویسه‌ها روی آن اعمال گردید.\n' +
          '«ی» و «ک» عربی به معادل‌های استاندارد فارسی تبدیل شده‌اند.\n' +
          'جهت اطمینان در اسناد رسمی، بازبینی نهایی توصیه می‌شود.';
        botCaption = 
          '✅ فایل Word با موفقیت ساخته شد.\n\n' +
          '📄 تعداد صفحات: ۱ صفحه\n' +
          '🔍 نوع سند: اسکن‌شده (با OCR استخراج شد)\n' +
          '⚠️ برای فایل‌های اسکن‌شده یا جدول‌های پیچیده، بازبینی نهایی توصیه می‌شود.';
      }

      // Generate real DOCX blob
      const docxBlob = await generatePersianDocx(sampleTitle, sampleContent);
      const downloadUrl = URL.createObjectURL(docxBlob);

      setIsProcessing(false);
      addMessage({
        sender: 'bot',
        text: botCaption,
        documentName: filename.replace('.pdf', '.docx'),
        documentSize: '22.4 KB',
        docxDownloadUrl: downloadUrl,
      });
    }, 1800);
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: '1',
        sender: 'bot',
        text: 'سلام! به ربات تبدیل PDF فارسی به Word خوش آمدید. 📄➡️📝\n\n«فایل PDF فارسی خود را بفرستید تا نسخه Word آن را دریافت کنید.»\n\nبرای مشاهده راهنما دستور /help را ارسال کنید.',
        timestamp: '۱۰:۰۰',
      }
    ]);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 text-right" dir="rtl">
      {/* Simulation Controls Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-bold text-slate-800 text-base flex items-center gap-2">
            <Bot className="w-5 h-5 text-sky-600" />
            شبیه‌ساز تعاملی ربات تلگرام
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            تست جریان کاربری کامل بدون نیاز به اتصال مستقیم به تلگرام در این پنجره
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleResetChat}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-medium transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            شروع مجدد گفتگو
          </button>
        </div>
      </div>

      {/* Quick Action Chips */}
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-xs font-medium text-slate-500 ml-1">تست‌های سریع:</span>
        <button
          onClick={() => simulatePDFUpload('ai')}
          disabled={isProcessing}
          className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-xs transition-colors flex items-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-300" />
          ارسال PDF با هوش مصنوعی (Gemini Vision)
        </button>
        <button
          onClick={() => simulatePDFUpload('text')}
          disabled={isProcessing}
          className="px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 text-xs font-medium transition-colors flex items-center gap-1.5"
        >
          <FileText className="w-3.5 h-3.5" />
          ارسال PDF متن‌محور
        </button>
        <button
          onClick={() => simulatePDFUpload('scanned')}
          disabled={isProcessing}
          className="px-3 py-1.5 rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 text-xs font-medium transition-colors flex items-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5" />
          ارسال PDF اسکن‌شده (OCR)
        </button>
        <button
          onClick={() => simulatePDFUpload('encrypted')}
          disabled={isProcessing}
          className="px-3 py-1.5 rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 text-xs font-medium transition-colors flex items-center gap-1.5"
        >
          <AlertCircle className="w-3.5 h-3.5" />
          تست فایل رمزدار
        </button>
        <button
          onClick={() => simulatePDFUpload('invalid')}
          disabled={isProcessing}
          className="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 text-xs font-medium transition-colors flex items-center gap-1.5"
        >
          <AlertCircle className="w-3.5 h-3.5" />
          تست فایل غیر PDF
        </button>
        <button
          onClick={() => simulatePDFUpload('group')}
          disabled={isProcessing}
          className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 text-xs font-medium transition-colors flex items-center gap-1.5"
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          تست گارد گروه
        </button>
      </div>

      {/* Telegram Chat Frame */}
      <div className="bg-[#0e1621] rounded-2xl border border-slate-800 shadow-xl overflow-hidden flex flex-col h-[560px]">
        {/* Chat Header */}
        <div className="bg-[#17212b] px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-sky-600 to-blue-500 flex items-center justify-center text-white font-bold text-sm shadow-md">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-slate-100 text-sm flex items-center gap-2">
                ربات تبدیل PDF به Word
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              </div>
              <div className="text-xs text-slate-400">@persian_pdf_docx_bot • آنلاین</div>
            </div>
          </div>
          <div className="text-xs text-slate-400 bg-slate-800/60 px-2.5 py-1 rounded-full">
            چت خصوصی امن (End-to-End)
          </div>
        </div>

        {/* Chat Messages Body */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-[#0e1621]/90 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px]">
          {messages.map((msg) => {
            const isBot = msg.sender === 'bot';
            return (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${isBot ? 'justify-start' : 'justify-end'}`}
              >
                {isBot && (
                  <div className="w-8 h-8 rounded-full bg-sky-600/30 text-sky-400 flex items-center justify-center flex-shrink-0 text-xs mt-1 border border-sky-500/20">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-md ${
                    isBot
                      ? 'bg-[#182533] text-slate-100 rounded-tr-none border border-slate-700/50'
                      : 'bg-[#2b5278] text-white rounded-tl-none'
                  }`}
                >
                  {/* Document Attachment Presentation */}
                  {msg.documentName && (
                    <div className="mb-2 p-3 rounded-xl bg-black/20 border border-white/10 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-10 h-10 rounded-lg bg-sky-500/20 text-sky-300 flex items-center justify-center flex-shrink-0">
                          <FileText className="w-5 h-5" />
                        </div>
                        <div className="truncate">
                          <div className="text-xs font-semibold truncate text-slate-100">
                            {msg.documentName}
                          </div>
                          <div className="text-[11px] text-slate-400">{msg.documentSize}</div>
                        </div>
                      </div>

                      {msg.docxDownloadUrl && (
                        <a
                          href={msg.docxDownloadUrl}
                          download={msg.documentName}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors shadow-sm flex-shrink-0"
                        >
                          <Download className="w-3.5 h-3.5" />
                          دانلود DOCX
                        </a>
                      )}
                    </div>
                  )}

                  {/* Message Text */}
                  {msg.text && (
                    <div className="text-xs leading-relaxed whitespace-pre-line text-slate-200">
                      {msg.text}
                    </div>
                  )}

                  <div className="text-[10px] text-slate-400 text-left mt-1.5 flex items-center justify-end gap-1">
                    <span>{msg.timestamp}</span>
                    {!isBot && <CheckCircle2 className="w-3 h-3 text-sky-300" />}
                  </div>
                </div>

                {!isBot && (
                  <div className="w-8 h-8 rounded-full bg-slate-700 text-slate-200 flex items-center justify-center flex-shrink-0 text-xs mt-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}

          {isProcessing && (
            <div className="flex gap-2.5 justify-start">
              <div className="w-8 h-8 rounded-full bg-sky-600/30 text-sky-400 flex items-center justify-center flex-shrink-0 text-xs mt-1 border border-sky-500/20">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-[#182533] text-slate-300 rounded-2xl rounded-tr-none px-4 py-3 shadow-md border border-slate-700/50 flex items-center gap-3">
                <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
                <span className="text-xs">در حال پردازش ناهمگام در صف Celery و ساخت ساختار RTL Word...</span>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input Bar */}
        <div className="bg-[#17212b] p-3 border-t border-slate-800 flex items-center gap-2">
          <button
            onClick={() => simulatePDFUpload('text')}
            title="ارسال فایل نمونه"
            className="p-2 text-slate-400 hover:text-sky-400 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendText()}
            placeholder="پیام یا فرمانی بنویسید (/start, /help, /status)..."
            className="flex-1 bg-[#242f3d] text-slate-100 placeholder-slate-400 text-xs px-4 py-2.5 rounded-xl border border-transparent focus:border-sky-500 focus:outline-none"
          />

          <button
            onClick={() => handleSendText()}
            disabled={!inputText.trim()}
            className="p-2.5 bg-sky-600 hover:bg-sky-500 disabled:opacity-40 disabled:hover:bg-sky-600 text-white rounded-xl transition-colors shadow-sm"
          >
            <Send className="w-4 h-4 rotate-180" />
          </button>
        </div>
      </div>
    </div>
  );
};

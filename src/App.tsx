import React, { useState } from 'react';
import { 
  Bot, 
  Layers, 
  FileText, 
  Terminal, 
  FolderTree, 
  Server, 
  Sparkles,
  ShieldCheck
} from 'lucide-react';
import { ActiveTab } from './types';
import { ArchitectureView } from './components/ArchitectureView';
import { BotSimulator } from './components/BotSimulator';
import { LiveConverter } from './components/LiveConverter';
import { TestSuiteRunner } from './components/TestSuiteRunner';
import { FileViewer } from './components/FileViewer';
import { DeploymentGuide } from './components/DeploymentGuide';

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('architecture');

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800" dir="rtl">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-sky-500 flex items-center justify-center text-white shadow-md">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h1 className="font-bold text-slate-900 text-base leading-tight">
                  ربات تلگرام تبدیل PDF فارسی به Word (DOCX)
                </h1>
                <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                  <span>معماری صنعتی MVP</span>
                  <span>•</span>
                  <span className="text-emerald-600 font-medium">پشتیبانی واقعی RTL و BiDi</span>
                  <span>•</span>
                  <span>صف Celery و Redis</span>
                </div>
              </div>
            </div>

            {/* Status badge */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              آماده استقرار با Docker Compose
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 space-x-reverse overflow-x-auto no-scrollbar border-t border-slate-100 py-1.5">
            <button
              onClick={() => setActiveTab('architecture')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                activeTab === 'architecture'
                  ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Layers className="w-4 h-4" />
              معماری و تصمیم‌های تیم
            </button>

            <button
              onClick={() => setActiveTab('simulator')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                activeTab === 'simulator'
                  ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Bot className="w-4 h-4" />
              شبیه‌ساز ربات تلگرام
            </button>

            <button
              onClick={() => setActiveTab('converter')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                activeTab === 'converter'
                  ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              راستی‌آزمایی زنده و دانلود DOCX
            </button>

            <button
              onClick={() => setActiveTab('tests')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                activeTab === 'tests'
                  ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Terminal className="w-4 h-4" />
              تست‌های واحد و یکپارچه
            </button>

            <button
              onClick={() => setActiveTab('files')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                activeTab === 'files'
                  ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <FolderTree className="w-4 h-4" />
              کدهای منبع و ساختار
            </button>

            <button
              onClick={() => setActiveTab('deployment')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                activeTab === 'deployment'
                  ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Server className="w-4 h-4" />
              راهنمای استقرار سرور
            </button>
          </nav>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'architecture' && <ArchitectureView />}
        {activeTab === 'simulator' && <BotSimulator />}
        {activeTab === 'converter' && <LiveConverter />}
        {activeTab === 'tests' && <TestSuiteRunner />}
        {activeTab === 'files' && <FileViewer />}
        {activeTab === 'deployment' && <DeploymentGuide />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            تیم ارشد فنی: Product Manager • Backend Engineer • Persian OCR Specialist • DevOps • Security
          </div>
          <div className="font-mono text-slate-400" dir="ltr">
            Python 3.12 • Aiogram 3 • Celery 5 • Tesseract (fas) • python-docx
          </div>
        </div>
      </footer>
    </div>
  );
}

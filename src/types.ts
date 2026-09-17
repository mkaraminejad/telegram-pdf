export type ActiveTab = 'architecture' | 'simulator' | 'converter' | 'tests' | 'files' | 'deployment';

export interface TelegramMessage {
  id: string;
  sender: 'user' | 'bot';
  text?: string;
  documentName?: string;
  documentSize?: string;
  timestamp: string;
  isProcessing?: boolean;
  statusLabel?: string;
  docxDownloadUrl?: string;
}

export interface TestCaseResult {
  id: string;
  title: string;
  category: 'Normalizer' | 'BiDi' | 'Digits' | 'ZWNJ' | 'OpenXML DOCX' | 'Security';
  input: string;
  expected: string;
  actual: string;
  passed: boolean;
  notes: string;
}

export interface ProjectFile {
  path: string;
  description: string;
  category: 'bot' | 'services' | 'handlers' | 'docker' | 'tests' | 'docs';
  code: string;
}

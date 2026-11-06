export interface Job {
  id: string;
  documentId: string;
  filename: string;
  fileSize: number;
  sha256: string;
  status: 'QUEUED' | 'INSPECTING' | 'CONVERTING' | 'OCR_PROCESSING' | 'NORMALIZING' | 'VALIDATING' | 'COMPLETED' | 'FAILED' | 'CANCELED';
  converter: string;
  ocrLanguages: string;
  documentLanguage?: string;
  forceOcr: boolean;
  progress: number;
  currentStep: string;
  errorMessage?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export interface DocumentMeta {
  id: string;
  jobId?: string;
  title: string;
  filename: string;
  sha256: string;
  language: string;
  pageCount: number;
  currentRevision: number;
  qualityStatus: 'PASS' | 'WARNING' | 'REQUIRES_REVIEW' | 'FAILED';
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown>;
}

export interface TextQuote {
  exact: string;
  prefix: string;
  suffix: string;
}

export interface TextPosition {
  start: number;
  end: number;
  unit: 'unicode-codepoint' | 'utf16-codeunit';
}

export interface Highlight {
  id: string;
  documentId: string;
  revision: number;
  blockIds: string[];
  quote: TextQuote;
  position: TextPosition;
  color: string;
  note?: string;
  resolved: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface QualityMetric {
  name: string;
  score: number;
  passed: boolean;
  details: string;
}

export interface QualityReport {
  documentId: string;
  overallStatus: 'PASS' | 'WARNING' | 'REQUIRES_REVIEW' | 'FAILED';
  textSelectabilityScore: number;
  unicodeIntegrityScore: number;
  structuralScore: number;
  metrics: QualityMetric[];
  warnings: string[];
  diagnostics: Record<string, unknown>;
}

export interface ConverterInfo {
  name: string;
  available: boolean;
  version?: string;
  description: string;
}

export interface LanguageDetail {
  code: string;
  name: string;
  installed: boolean;
}

export interface SystemCapabilities {
  platform: string;
  cpuCount: number;
  totalRamGb: number;
  gpuAvailable: boolean;
  gpuName: string;
  gpuMemoryMb: number;
  recommendedDevice: string;
  defaultWorkers: number;
  installedOcrLanguages: string[];
  languageDetails?: LanguageDetail[];
  converters: ConverterInfo[];
  defaultConverter: string;
}


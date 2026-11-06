import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud, FileText, X, Check, AlertCircle, Settings2,
  Globe, Search, Sparkles, ChevronDown, ChevronUp
} from 'lucide-react';
import { api } from '../services/api';
import { LanguageDetail } from '../types';

const POPULAR_DOC_LANGUAGES = [
  { code: 'AUTO', name: 'Auto-Detect (Recommended)', bcp47: 'auto' },
  { code: 'en', name: 'English', bcp47: 'en-US' },
  { code: 'hi', name: 'Hindi (हिन्दी)', bcp47: 'hi-IN' },
  { code: 'ta', name: 'Tamil (தமிழ்)', bcp47: 'ta-IN' },
  { code: 'te', name: 'Telugu (తెలుగు)', bcp47: 'te-IN' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)', bcp47: 'kn-IN' },
  { code: 'ml', name: 'Malayalam (മലയാളം)', bcp47: 'ml-IN' },
  { code: 'bn', name: 'Bengali (বাংলা)', bcp47: 'bn-BD' },
  { code: 'mr', name: 'Marathi (मराठी)', bcp47: 'mr-IN' },
  { code: 'gu', name: 'Gujarati (ગુજરાતી)', bcp47: 'gu-IN' },
  { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)', bcp47: 'pa-IN' },
  { code: 'sa', name: 'Sanskrit (संस्कृतम्)', bcp47: 'sa-IN' },
  { code: 'ar', name: 'Arabic (العربية)', bcp47: 'ar-SA' },
  { code: 'ur', name: 'Urdu (اردو)', bcp47: 'ur-PK' },
  { code: 'ru', name: 'Russian (Русский)', bcp47: 'ru-RU' },
  { code: 'zh', name: 'Chinese (简体中文)', bcp47: 'zh-CN' },
  { code: 'ja', name: 'Japanese (日本語)', bcp47: 'ja-JP' },
  { code: 'ko', name: 'Korean (한국어)', bcp47: 'ko-KR' },
  { code: 'es', name: 'Spanish (Español)', bcp47: 'es-ES' },
  { code: 'fr', name: 'French (Français)', bcp47: 'fr-FR' },
  { code: 'de', name: 'German (Deutsch)', bcp47: 'de-DE' },
  { code: 'he', name: 'Hebrew (עברית)', bcp47: 'he-IL' },
  { code: 'th', name: 'Thai (ไทย)', bcp47: 'th-TH' },
  { code: 'fa', name: 'Persian (فارسی)', bcp47: 'fa-IR' },
  { code: 'vi', name: 'Vietnamese (Tiếng Việt)', bcp47: 'vi-VN' },
];

const POPULAR_OCR_LANGS = [
  { code: 'eng', name: 'English' },
  { code: 'tam', name: 'Tamil (தமிழ்)' },
  { code: 'hin', name: 'Hindi (हिन्दी)' },
  { code: 'tel', name: 'Telugu (తెలుగు)' },
  { code: 'mal', name: 'Malayalam (മലയാളം)' },
  { code: 'kan', name: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ben', name: 'Bengali (বাংলা)' },
  { code: 'mar', name: 'Marathi (मराठी)' },
  { code: 'guj', name: 'Gujarati (ગુજરાતી)' },
  { code: 'pan', name: 'Punjabi (ਪੰਜਾਬੀ)' },
  { code: 'san', name: 'Sanskrit (संस्कृतम्)' },
  { code: 'ara', name: 'Arabic (العربية)' },
  { code: 'urd', name: 'Urdu (اردو)' },
  { code: 'rus', name: 'Russian (Русский)' },
  { code: 'heb', name: 'Hebrew (עברית)' },
  { code: 'tha', name: 'Thai (ไทย)' },
  { code: 'chi_sim', name: 'Chinese Simp (简体)' },
  { code: 'jpn', name: 'Japanese (日本語)' },
  { code: 'kor', name: 'Korean (한국어)' },
  { code: 'fra', name: 'French' },
  { code: 'deu', name: 'German' },
  { code: 'spa', name: 'Spanish' },
];

export const UploadScreen: React.FC = () => {
  const navigate = useNavigate();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [converter, setConverter] = useState('AUTO');

  // Document Language State
  const [docLangMode, setDocLangMode] = useState<'AUTO' | 'PRESET' | 'CUSTOM'>('AUTO');
  const [selectedDocLang, setSelectedDocLang] = useState('AUTO');
  const [customDocLang, setCustomDocLang] = useState('');

  // OCR Language State
  const [ocrAutoDetect, setOcrAutoDetect] = useState(false);
  const [selectedOcrLangs, setSelectedOcrLangs] = useState<string[]>(['eng', 'tam', 'hin']);
  const [customOcrInput, setCustomOcrInput] = useState('');
  const [installedLangs, setInstalledLangs] = useState<LanguageDetail[]>([]);
  const [langSearchQuery, setLangSearchQuery] = useState('');
  const [showAllOcrLangs, setShowAllOcrLangs] = useState(false);

  const [forceOcr, setForceOcr] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load installed OCR languages from backend capabilities
  useEffect(() => {
    api.getCapabilities()
      .then((caps) => {
        if (caps.languageDetails && caps.languageDetails.length > 0) {
          setInstalledLangs(caps.languageDetails);
        } else if (caps.installedOcrLanguages) {
          setInstalledLangs(
            caps.installedOcrLanguages.map((code) => ({
              code,
              name: code,
              installed: true,
            }))
          );
        }
      })
      .catch(() => {
        // Fallback to default popular list if offline
      });
  }, []);

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = (files: File[]) => {
    setErrorMsg(null);
    const valid = files.filter((f) => f.name.toLowerCase().endsWith('.pdf'));
    if (valid.length < files.length) {
      setErrorMsg('Some selected files were ignored because they are not valid PDF documents.');
    }
    setSelectedFiles((prev) => [...prev, ...valid]);
  };

  const removeFile = (idx: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const toggleOcrLanguage = (code: string) => {
    setOcrAutoDetect(false);
    setSelectedOcrLangs((prev) =>
      prev.includes(code)
        ? prev.length > 1
          ? prev.filter((c) => c !== code)
          : prev
        : [...prev, code]
    );
  };

  // Filtered installed languages list
  const filteredInstalledLangs = useMemo(() => {
    if (!langSearchQuery.trim()) return installedLangs;
    const q = langSearchQuery.toLowerCase();
    return installedLangs.filter(
      (l) => l.code.toLowerCase().includes(q) || l.name.toLowerCase().includes(q)
    );
  }, [installedLangs, langSearchQuery]);

  // Compute final effective OCR languages string
  const effectiveOcrString = useMemo(() => {
    if (ocrAutoDetect) return 'AUTO';
    if (customOcrInput.trim()) return customOcrInput.trim();
    return selectedOcrLangs.join('+');
  }, [ocrAutoDetect, customOcrInput, selectedOcrLangs]);

  // Compute final effective Document Language string
  const effectiveDocLangString = useMemo(() => {
    if (docLangMode === 'AUTO') return 'AUTO';
    if (docLangMode === 'CUSTOM') return customDocLang.trim() || 'AUTO';
    return selectedDocLang;
  }, [docLangMode, customDocLang, selectedDocLang]);

  const handleUploadSubmit = async () => {
    if (selectedFiles.length === 0) {
      setErrorMsg('Please select at least one PDF file to upload.');
      return;
    }

    setUploading(true);
    setErrorMsg(null);

    try {
      await api.uploadJobs(
        selectedFiles,
        converter,
        effectiveOcrString,
        forceOcr,
        effectiveDocLangString
      );
      navigate('/queue');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed. Check server status.';
      setErrorMsg(msg);
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Batch PDF Upload</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload one or more PDF documents in any language. Supports any OCR language code and universal Unicode script detection.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-center">
          <AlertCircle className="w-5 h-5 mr-2 text-red-500 flex-shrink-0" />
          {errorMsg}
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
        className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-green-500 bg-white transition cursor-pointer shadow-sm"
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          multiple
          accept=".pdf"
          className="hidden"
          onChange={handleFileInput}
        />
        <div className="w-14 h-14 bg-green-50 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-8 h-8" />
        </div>
        <h3 className="text-base font-semibold text-gray-900">Click to upload or drag and drop PDFs</h3>
        <p className="text-xs text-gray-500 mt-1">Accepts digital, scanned, or mixed PDFs up to 150MB</p>
      </div>

      {/* Selected File List */}
      {selectedFiles.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 divide-y divide-gray-100 shadow-sm">
          <div className="text-sm font-semibold text-gray-700 pb-2">
            Selected Documents ({selectedFiles.length})
          </div>
          {selectedFiles.map((f, i) => (
            <div key={`${f.name}-${i}`} className="py-2.5 flex items-center justify-between text-sm">
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-gray-400" />
                <span className="font-medium text-gray-800">{f.name}</span>
                <span className="text-xs text-gray-400">({(f.size / (1024 * 1024)).toFixed(2)} MB)</span>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(i);
                }}
                className="text-gray-400 hover:text-red-500 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Conversion Options */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-6 shadow-sm">
        <h3 className="text-base font-semibold text-gray-900 flex items-center">
          <Settings2 className="w-4 h-4 mr-2 text-gray-500" />
          Conversion & Language Settings
        </h3>

        {/* 1. Document Language Selection */}
        <div className="space-y-3 pb-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-gray-700 uppercase tracking-wider flex items-center">
              <Globe className="w-4 h-4 mr-1.5 text-green-600" />
              Document Language (Can be any language)
            </label>
            <div className="flex items-center space-x-2 text-xs">
              <button
                type="button"
                onClick={() => {
                  setDocLangMode('AUTO');
                  setSelectedDocLang('AUTO');
                }}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  docLangMode === 'AUTO'
                    ? 'bg-green-100 text-green-800'
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                Auto-Detect
              </button>
              <button
                type="button"
                onClick={() => setDocLangMode('PRESET')}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  docLangMode === 'PRESET'
                    ? 'bg-green-100 text-green-800'
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                Preset List
              </button>
              <button
                type="button"
                onClick={() => setDocLangMode('CUSTOM')}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  docLangMode === 'CUSTOM'
                    ? 'bg-green-100 text-green-800'
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                Custom Code
              </button>
            </div>
          </div>

          {docLangMode === 'AUTO' && (
            <div className="p-3 bg-green-50/70 border border-green-200 rounded-lg text-xs text-green-800 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-green-600 flex-shrink-0" />
              <span>
                <strong>Smart Unicode Script Detection:</strong> Antigravity automatically detects the script (Devanagari, Tamil, Cyrillic, Arabic, Hebrew, CJK, etc.) and tags semantic HTML with the correct BCP-47 language and RTL/LTR direction.
              </span>
            </div>
          )}

          {docLangMode === 'PRESET' && (
            <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto p-1 border border-gray-100 rounded-lg">
              {POPULAR_DOC_LANGUAGES.map((l) => (
                <button
                  key={l.code}
                  type="button"
                  onClick={() => setSelectedDocLang(l.code)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium border transition ${
                    selectedDocLang === l.code
                      ? 'bg-green-600 text-white border-green-600'
                      : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  {l.name}
                </button>
              ))}
            </div>
          )}

          {docLangMode === 'CUSTOM' && (
            <div className="space-y-1">
              <input
                type="text"
                placeholder="Enter any BCP-47 or ISO language tag (e.g. ru-RU, th, vi, fa-IR, de-CH, sa)"
                value={customDocLang}
                onChange={(e) => setCustomDocLang(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
              />
              <p className="text-xs text-gray-500">
                Any valid ISO 639 code or IETF BCP-47 tag will be embedded directly into HTML output and metadata.
              </p>
            </div>
          )}
        </div>

        {/* 2. Engine Selection */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">
            Conversion Engine Strategy
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { id: 'AUTO', name: 'AUTO (Recommended)', desc: 'Smart inspection & fallback' },
              { id: 'MARKER', name: 'Marker', desc: 'Surya layout models' },
              { id: 'DOCLING', name: 'Docling', desc: 'IBM deep document parse' },
              { id: 'NATIVE', name: 'Native Hybrid', desc: 'PyMuPDF + Tesseract' },
            ].map((eng) => (
              <button
                key={eng.id}
                type="button"
                onClick={() => setConverter(eng.id)}
                className={`p-3 rounded-xl border text-left transition ${
                  converter === eng.id
                    ? 'border-green-600 bg-green-50 text-green-900 ring-2 ring-green-600/20'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <div className="text-sm font-semibold">{eng.name}</div>
                <div className="text-xs text-gray-500 mt-1">{eng.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* 3. OCR Language Selection */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-gray-700 uppercase tracking-wider flex items-center">
              Target OCR Languages (Can be any language)
            </label>
            <button
              type="button"
              onClick={() => {
                setOcrAutoDetect(!ocrAutoDetect);
                if (!ocrAutoDetect) {
                  setCustomOcrInput('');
                }
              }}
              className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium transition ${
                ocrAutoDetect
                  ? 'bg-green-100 text-green-800 border border-green-300'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 mr-1 text-green-600" />
              {ocrAutoDetect ? 'Auto-Detect OCR Enabled' : 'Enable OCR Auto-Detect'}
            </button>
          </div>

          {ocrAutoDetect ? (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-800">
              Antigravity will inspect the PDF first and dynamically activate the required OCR language packs (Hindi, Tamil, Russian, Arabic, etc.) corresponding to detected fonts and scripts.
            </div>
          ) : (
            <>
              {/* Popular Quick-Select Chips */}
              <div>
                <span className="text-xs text-gray-400 block mb-1.5">Common Languages:</span>
                <div className="flex flex-wrap gap-1.5">
                  {POPULAR_OCR_LANGS.map((lang) => {
                    const active = selectedOcrLangs.includes(lang.code) && !customOcrInput.trim();
                    return (
                      <button
                        key={lang.code}
                        type="button"
                        onClick={() => {
                          setCustomOcrInput('');
                          toggleOcrLanguage(lang.code);
                        }}
                        className={`inline-flex items-center px-2.5 py-1.5 rounded-lg text-xs font-medium border transition ${
                          active
                            ? 'bg-green-600 text-white border-green-600 shadow-sm'
                            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                        }`}
                      >
                        {active && <Check className="w-3.5 h-3.5 mr-1" />}
                        {lang.name}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Custom or Combined OCR Input */}
              <div className="pt-2">
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Custom OCR Language Combination (Any installed or custom pack):
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="e.g. rus+eng, vie+fra, heb+ara, tha+eng, nep+san"
                    value={customOcrInput}
                    onChange={(e) => setCustomOcrInput(e.target.value)}
                    className="flex-1 px-3 py-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
                  />
                  {customOcrInput && (
                    <button
                      type="button"
                      onClick={() => setCustomOcrInput('')}
                      className="px-2.5 py-1 text-xs text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg"
                    >
                      Reset to Selection
                    </button>
                  )}
                </div>
              </div>

              {/* Collapsible search for all 125+ installed languages */}
              <div className="pt-1">
                <button
                  type="button"
                  onClick={() => setShowAllOcrLangs(!showAllOcrLangs)}
                  className="text-xs font-medium text-green-700 hover:text-green-800 flex items-center space-x-1"
                >
                  <span>{showAllOcrLangs ? 'Hide' : 'Browse All'} Installed Tesseract Languages ({installedLangs.length || '125+'})</span>
                  {showAllOcrLangs ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>

                {showAllOcrLangs && (
                  <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-xl space-y-2">
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-2.5" />
                      <input
                        type="text"
                        placeholder="Filter languages by name or code (e.g. thai, russian, greek, hebrew)..."
                        value={langSearchQuery}
                        onChange={(e) => setLangSearchQuery(e.target.value)}
                        className="w-full pl-8 pr-3 py-1.5 text-xs bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5 max-h-48 overflow-y-auto pr-1">
                      {filteredInstalledLangs.map((item) => {
                        const isSelected = selectedOcrLangs.includes(item.code);
                        return (
                          <button
                            key={item.code}
                            type="button"
                            onClick={() => {
                              setCustomOcrInput('');
                              toggleOcrLanguage(item.code);
                            }}
                            className={`px-2 py-1 rounded text-left text-xs truncate border transition ${
                              isSelected
                                ? 'bg-green-600 text-white border-green-600'
                                : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-100'
                            }`}
                            title={`${item.name} (${item.code})`}
                          >
                            <span className="font-mono text-[10px] opacity-75 mr-1">{item.code}:</span>
                            {item.name}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              {/* Active Selection Summary */}
              <div className="text-xs text-gray-500 flex items-center space-x-1">
                <span>Active OCR Config:</span>
                <span className="font-mono font-medium text-gray-800 bg-gray-100 px-2 py-0.5 rounded">
                  {effectiveOcrString}
                </span>
                <span className="text-gray-400">| Document Lang:</span>
                <span className="font-mono font-medium text-gray-800 bg-gray-100 px-2 py-0.5 rounded">
                  {effectiveDocLangString}
                </span>
              </div>
            </>
          )}
        </div>

        {/* 4. Force OCR Toggle */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div>
            <div className="text-sm font-medium text-gray-900">Force OCR Processing</div>
            <div className="text-xs text-gray-500">
              Run Tesseract OCR on all pages even if digital text exists (useful for corrupted CMaps)
            </div>
          </div>
          <button
            type="button"
            onClick={() => setForceOcr(!forceOcr)}
            className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
              forceOcr ? 'bg-green-600' : 'bg-gray-200'
            }`}
          >
            <div
              className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                forceOcr ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="button"
        disabled={selectedFiles.length === 0 || uploading}
        onClick={handleUploadSubmit}
        className={`w-full py-3.5 px-4 rounded-xl font-semibold text-white text-sm shadow transition flex items-center justify-center ${
          selectedFiles.length === 0 || uploading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700'
        }`}
      >
        {uploading ? (
          <span>Queueing {selectedFiles.length} Documents...</span>
        ) : (
          <span>Start Converting ({selectedFiles.length} files)</span>
        )}
      </button>
    </div>
  );
};

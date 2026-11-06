import React, { useState, useEffect, useMemo } from 'react';
import {
  UploadCloud,
  FileText,
  X,
  AlertCircle,
  Settings2,
  Globe,
  Search,
  Sparkles,
} from 'lucide-react';
import { api } from '../../services/api';
import { LanguageDetail } from '../../types';
import { POPULAR_DOC_LANGUAGES, POPULAR_OCR_LANGS } from '../../constants/languages';

interface SidebarUploadProps {
  onUploadSuccess: () => void;
}

export const SidebarUpload: React.FC<SidebarUploadProps> = ({ onUploadSuccess }) => {
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
      .catch(() => null);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).filter((f) => f.name.toLowerCase().endsWith('.pdf'));
      setSelectedFiles((prev) => [...prev, ...files]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const files = Array.from(e.dataTransfer.files).filter((f) => f.name.toLowerCase().endsWith('.pdf'));
      setSelectedFiles((prev) => [...prev, ...files]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const toggleOcrLang = (code: string) => {
    setSelectedOcrLangs((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const handleAddCustomOcr = () => {
    const trimmed = customOcrInput.trim().toLowerCase();
    if (!trimmed) return;
    const codes = trimmed
      .split(/[+,;\s]+/)
      .map((c) => c.trim())
      .filter(Boolean);

    setSelectedOcrLangs((prev) => {
      const set = new Set([...prev, ...codes]);
      return Array.from(set);
    });
    setCustomOcrInput('');
  };

  const effectiveDocLanguage = useMemo(() => {
    if (docLangMode === 'AUTO') return 'AUTO';
    if (docLangMode === 'CUSTOM') {
      const trimmed = customDocLang.trim();
      return trimmed || 'AUTO';
    }
    return selectedDocLang;
  }, [docLangMode, selectedDocLang, customDocLang]);

  const effectiveOcrLanguages = useMemo(() => {
    if (ocrAutoDetect) return 'auto';
    return selectedOcrLangs.length > 0 ? selectedOcrLangs.join('+') : 'eng';
  }, [ocrAutoDetect, selectedOcrLangs]);

  const filteredInstalledLangs = useMemo(() => {
    if (!langSearchQuery.trim()) return installedLangs;
    const q = langSearchQuery.toLowerCase();
    return installedLangs.filter(
      (l) => l.code.toLowerCase().includes(q) || l.name.toLowerCase().includes(q)
    );
  }, [installedLangs, langSearchQuery]);

  const handleSubmit = async () => {
    if (selectedFiles.length === 0) return;
    setUploading(true);
    setErrorMsg(null);

    try {
      await api.uploadJobs(
        selectedFiles,
        converter,
        effectiveOcrLanguages,
        forceOcr,
        effectiveDocLanguage
      );
      setSelectedFiles([]);
      onUploadSuccess();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed. Check server connection.';
      setErrorMsg(msg);
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto p-3 space-y-4">
      {/* Drop Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className="border-2 border-dashed border-gray-300 hover:border-green-500 rounded-xl p-4 text-center bg-gray-50/50 hover:bg-green-50/30 transition cursor-pointer"
        onClick={() => document.getElementById('sidebar-file-upload')?.click()}
      >
        <UploadCloud className="w-8 h-8 mx-auto text-green-600 mb-2" />
        <p className="text-xs font-semibold text-gray-800">
          Click or Drag & Drop PDFs
        </p>
        <p className="text-[10px] text-gray-500 mt-0.5">
          Up to 150MB • All scripts & languages supported
        </p>
        <input
          id="sidebar-file-upload"
          type="file"
          multiple
          accept=".pdf"
          className="hidden"
          onChange={handleFileSelect}
        />
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-gray-600 uppercase tracking-wider block">
            Selected Files ({selectedFiles.length})
          </span>
          <div className="max-h-28 overflow-y-auto space-y-1">
            {selectedFiles.map((file, idx) => (
              <div
                key={`${file.name}-${idx}`}
                className="flex items-center justify-between bg-white border border-gray-200 rounded-lg px-2.5 py-1 text-xs"
              >
                <div className="flex items-center space-x-1.5 truncate">
                  <FileText className="w-3.5 h-3.5 text-green-600 flex-shrink-0" />
                  <span className="truncate">{file.name}</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(idx)}
                  className="text-gray-400 hover:text-red-500 p-0.5"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Document Language Section */}
      <div className="bg-white border border-gray-200 rounded-xl p-3 space-y-2.5 shadow-2xs">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-gray-800 flex items-center">
            <Globe className="w-3.5 h-3.5 text-green-600 mr-1.5" />
            Document Language
          </label>
        </div>

        {/* Mode Selector */}
        <div className="grid grid-cols-3 gap-1 bg-gray-100 p-0.5 rounded-lg text-[11px]">
          <button
            type="button"
            onClick={() => setDocLangMode('AUTO')}
            className={`py-1 rounded font-medium transition ${
              docLangMode === 'AUTO'
                ? 'bg-white text-green-700 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Auto
          </button>
          <button
            type="button"
            onClick={() => setDocLangMode('PRESET')}
            className={`py-1 rounded font-medium transition ${
              docLangMode === 'PRESET'
                ? 'bg-white text-green-700 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Select
          </button>
          <button
            type="button"
            onClick={() => setDocLangMode('CUSTOM')}
            className={`py-1 rounded font-medium transition ${
              docLangMode === 'CUSTOM'
                ? 'bg-white text-green-700 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Custom
          </button>
        </div>

        {docLangMode === 'PRESET' && (
          <select
            value={selectedDocLang}
            onChange={(e) => setSelectedDocLang(e.target.value)}
            className="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-800 focus:outline-none focus:ring-1 focus:ring-green-500"
          >
            {POPULAR_DOC_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        )}

        {docLangMode === 'CUSTOM' && (
          <input
            type="text"
            value={customDocLang}
            onChange={(e) => setCustomDocLang(e.target.value)}
            placeholder="e.g. sa, ur, fa, bo, my"
            className="w-full text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 bg-white text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-green-500"
          />
        )}
      </div>

      {/* OCR Languages Section */}
      <div className="bg-white border border-gray-200 rounded-xl p-3 space-y-2.5 shadow-2xs">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-gray-800 flex items-center">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600 mr-1.5" />
            OCR Languages
          </label>
          <label className="flex items-center space-x-1 cursor-pointer text-[11px] text-gray-500">
            <input
              type="checkbox"
              checked={ocrAutoDetect}
              onChange={(e) => setOcrAutoDetect(e.target.checked)}
              className="rounded text-green-600 focus:ring-green-500 h-3 w-3"
            />
            <span>Auto</span>
          </label>
        </div>

        {!ocrAutoDetect && (
          <>
            {/* Quick Presets */}
            <div className="flex flex-wrap gap-1">
              {POPULAR_OCR_LANGS.slice(0, 10).map((l) => {
                const isSelected = selectedOcrLangs.includes(l.code);
                return (
                  <button
                    key={l.code}
                    type="button"
                    onClick={() => toggleOcrLang(l.code)}
                    className={`px-2 py-0.5 rounded text-[10px] font-medium transition ${
                      isSelected
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {l.code}
                  </button>
                );
              })}
            </div>

            {/* Custom OCR Input */}
            <div className="flex space-x-1 pt-1">
              <input
                type="text"
                value={customOcrInput}
                onChange={(e) => setCustomOcrInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddCustomOcr();
                  }
                }}
                placeholder="+ Add code (e.g. kan+mal)"
                className="flex-1 text-[11px] border border-gray-200 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-green-500"
              />
              <button
                type="button"
                onClick={handleAddCustomOcr}
                className="px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-[11px] font-medium"
              >
                Add
              </button>
            </div>

            {/* Toggle 125+ OCR Languages Search */}
            <div className="pt-1">
              <button
                type="button"
                onClick={() => setShowAllOcrLangs((prev) => !prev)}
                className="text-[11px] text-indigo-600 hover:underline flex items-center"
              >
                {showAllOcrLangs ? 'Hide full languages list' : `Search ${installedLangs.length || '125+'} installed languages`}
              </button>
              {showAllOcrLangs && (
                <div className="mt-1 space-y-1 bg-gray-50 p-2 rounded-lg border border-gray-200">
                  <div className="relative">
                    <Search className="w-3 h-3 text-gray-400 absolute left-2 top-2" />
                    <input
                      type="text"
                      value={langSearchQuery}
                      onChange={(e) => setLangSearchQuery(e.target.value)}
                      placeholder="Filter languages..."
                      className="w-full pl-6 pr-2 py-1 text-[10px] border border-gray-200 rounded bg-white"
                    />
                  </div>
                  <div className="max-h-24 overflow-y-auto space-y-0.5 text-[10px]">
                    {filteredInstalledLangs.slice(0, 30).map((l) => (
                      <div
                        key={l.code}
                        onClick={() => toggleOcrLang(l.code)}
                        className={`px-1.5 py-0.5 rounded cursor-pointer flex justify-between ${
                          selectedOcrLangs.includes(l.code)
                            ? 'bg-green-100 text-green-800 font-semibold'
                            : 'hover:bg-gray-100 text-gray-700'
                        }`}
                      >
                        <span>{l.name}</span>
                        <span className="font-mono text-gray-400">{l.code}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Engine Selection & Force OCR */}
      <div className="bg-white border border-gray-200 rounded-xl p-3 space-y-2.5 shadow-2xs">
        <div>
          <label className="text-xs font-semibold text-gray-800 flex items-center mb-1">
            <Settings2 className="w-3.5 h-3.5 text-gray-600 mr-1.5" />
            Converter Engine
          </label>
          <select
            value={converter}
            onChange={(e) => setConverter(e.target.value)}
            className="w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white text-gray-800 focus:outline-none focus:ring-1 focus:ring-green-500"
          >
            <option value="AUTO">AUTO (Smart Auto-Select)</option>
            <option value="NATIVE">NATIVE (PyMuPDF + Tesseract)</option>
            <option value="MARKER">MARKER (Deep Learning)</option>
            <option value="DOCLING">DOCLING (IBM Parser)</option>
          </select>
        </div>

        <div className="pt-1">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={forceOcr}
              onChange={(e) => setForceOcr(e.target.checked)}
              className="rounded text-green-600 focus:ring-green-500 h-3.5 w-3.5"
            />
            <span className="text-xs text-gray-700">
              Force Full OCR (Scanned PDF mode)
            </span>
          </label>
        </div>
      </div>

      {/* Error message */}
      {errorMsg && (
        <div className="text-xs text-red-600 bg-red-50 p-2.5 rounded-xl border border-red-200 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Convert Button */}
      <button
        type="button"
        disabled={selectedFiles.length === 0 || uploading}
        onClick={handleSubmit}
        className={`w-full py-2.5 px-4 rounded-xl font-bold text-xs shadow transition flex items-center justify-center space-x-1.5 ${
          selectedFiles.length === 0 || uploading
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-green-600 hover:bg-green-700 text-white shadow-green-600/20'
        }`}
      >
        <UploadCloud className="w-4 h-4" />
        <span>{uploading ? 'Submitting Jobs...' : `Convert ${selectedFiles.length} PDF${selectedFiles.length === 1 ? '' : 's'}`}</span>
      </button>
    </div>
  );
};

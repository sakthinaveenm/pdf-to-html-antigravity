import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, X, Check, AlertCircle, Settings2 } from 'lucide-react';
import { api } from '../services/api';

const LANGUAGE_OPTIONS = [
  { code: 'eng', name: 'English' },
  { code: 'tam', name: 'Tamil (தமிழ்)' },
  { code: 'hin', name: 'Hindi (हिन्दी)' },
  { code: 'tel', name: 'Telugu (తెలుగు)' },
  { code: 'mal', name: 'Malayalam (മലയാളം)' },
  { code: 'kan', name: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ben', name: 'Bengali (বাংলা)' },
  { code: 'mar', name: 'Marathi (मराठी)' },
  { code: 'guj', name: 'Gujarati (ગુજરાતી)' },
  { code: 'ara', name: 'Arabic (العربية)' },
  { code: 'urd', name: 'Urdu (اردو)' },
  { code: 'chi_sim', name: 'Chinese (简体中文)' },
  { code: 'jpn', name: 'Japanese (日本語)' },
  { code: 'kor', name: 'Korean (한국어)' },
  { code: 'fra', name: 'French (Français)' },
  { code: 'deu', name: 'German (Deutsch)' },
  { code: 'spa', name: 'Spanish (Español)' },
];

export const UploadScreen: React.FC = () => {
  const navigate = useNavigate();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [converter, setConverter] = useState('AUTO');
  const [selectedLangs, setSelectedLangs] = useState<string[]>(['eng', 'tam', 'hin']);
  const [forceOcr, setForceOcr] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

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

  const toggleLanguage = (code: string) => {
    setSelectedLangs((prev) =>
      prev.includes(code) ? (prev.length > 1 ? prev.filter((c) => c !== code) : prev) : [...prev, code]
    );
  };

  const handleUploadSubmit = async () => {
    if (selectedFiles.length === 0) {
      setErrorMsg('Please select at least one PDF file to upload.');
      return;
    }

    setUploading(true);
    setErrorMsg(null);

    try {
      const ocrLangsString = selectedLangs.join('+');
      await api.uploadJobs(selectedFiles, converter, ocrLangsString, forceOcr);
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
          Upload one or more PDF documents in any language. Each document is queued and processed independently.
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
        className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-green-500 bg-white transition cursor-pointer"
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
        <div className="bg-white rounded-xl border border-gray-200 p-4 divide-y divide-gray-100">
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
                onClick={() => removeFile(i)}
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
          Conversion & OCR Settings
        </h3>

        {/* Engine Selection */}
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

        {/* OCR Language Selection */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">
            Target OCR Languages (Multiple allowed)
          </label>
          <div className="flex flex-wrap gap-2">
            {LANGUAGE_OPTIONS.map((lang) => {
              const active = selectedLangs.includes(lang.code);
              return (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => toggleLanguage(lang.code)}
                  className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                    active
                      ? 'bg-green-600 text-white border-green-600'
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

        {/* Force OCR Toggle */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
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


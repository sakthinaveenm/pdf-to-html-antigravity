import React from 'react';
import {
  UploadCloud,
  Cpu,
  ArrowRight,
  BookOpen,
} from 'lucide-react';
import { DocumentMeta, SystemCapabilities } from '../../types';

interface EmptyWorkspaceProps {
  documents: DocumentMeta[];
  caps: SystemCapabilities | null;
  onSelectDocument: (docId: string) => void;
  onOpenUpload: () => void;
}

export const EmptyWorkspace: React.FC<EmptyWorkspaceProps> = ({
  documents,
  caps,
  onSelectDocument,
  onOpenUpload,
}) => {
  return (
    <div className="flex-1 h-full overflow-y-auto bg-gray-50 p-6 flex flex-col items-center justify-center">
      <div className="max-w-3xl w-full space-y-6">
        {/* Hero Card */}
        <div className="bg-gradient-to-br from-green-800 via-emerald-800 to-teal-900 rounded-3xl p-8 text-white shadow-xl">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center text-white font-bold text-xl">
              Ω
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Multilingual PDF → Semantic HTML</h2>
              <p className="text-xs text-green-200">Local-First Document Workspace & Studio</p>
            </div>
          </div>

          <p className="text-sm text-green-100 leading-relaxed mb-6 max-w-xl">
            Convert any multilingual PDF—including scanned documents, complex Indic fonts (Hindi, Tamil, Sanskrit), Arabic RTL, and East Asian scripts—into clean, durable, accessible, and selectable HTML5.
          </p>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={onOpenUpload}
              className="inline-flex items-center px-5 py-2.5 rounded-xl bg-white text-green-900 font-bold text-xs shadow-md hover:bg-green-50 transition"
            >
              <UploadCloud className="w-4 h-4 mr-2 text-green-700" />
              Upload & Convert PDF
            </button>
            {documents.length > 0 && (
              <button
                onClick={() => onSelectDocument(documents[0].id)}
                className="inline-flex items-center px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/20 transition backdrop-blur-md"
              >
                <BookOpen className="w-4 h-4 mr-2" />
                Open Recent: {documents[0].title}
              </button>
            )}
          </div>
        </div>

        {/* Recent Documents Quick Grid */}
        {documents.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                Recent Converted Documents
              </h3>
              <span className="text-xs text-gray-400">{documents.length} available</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {documents.slice(0, 4).map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => onSelectDocument(doc.id)}
                  className="group p-3.5 rounded-xl border border-gray-200 hover:border-green-400 hover:bg-green-50/40 transition cursor-pointer flex items-center justify-between"
                >
                  <div className="min-w-0 flex-1 pr-2">
                    <h4 className="text-xs font-bold text-gray-900 truncate group-hover:text-green-800">
                      {doc.title}
                    </h4>
                    <p className="text-[11px] text-gray-500 truncate mt-0.5">{doc.filename}</p>
                    <div className="flex items-center space-x-2 mt-2 text-[10px] text-gray-400">
                      <span className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-700 uppercase font-semibold">
                        {doc.language || 'DOC'}
                      </span>
                      <span>{doc.pageCount} pages</span>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-green-600 group-hover:translate-x-0.5 transition" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Engine Specs */}
        {caps && (
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs">
            <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-3 flex items-center">
              <Cpu className="w-4 h-4 text-green-600 mr-2" />
              Local Hardware & OCR Pipeline
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div>
                <span className="text-gray-400 block text-[11px]">Platform</span>
                <span className="font-semibold text-gray-800">{caps.platform}</span>
                <p className="text-[11px] text-gray-500 mt-0.5">{caps.cpuCount} Cores • {caps.totalRamGb} GB RAM</p>
              </div>
              <div>
                <span className="text-gray-400 block text-[11px]">Primary Converter</span>
                <span className="font-semibold text-green-700">{caps.defaultConverter}</span>
                <p className="text-[11px] text-gray-500 mt-0.5">High-fidelity layout engine</p>
              </div>
              <div>
                <span className="text-gray-400 block text-[11px]">OCR Languages</span>
                <span className="font-semibold text-gray-800">{caps.installedOcrLanguages.length} Languages</span>
                <p className="text-[11px] text-gray-500 mt-0.5">Tesseract multi-script pack</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

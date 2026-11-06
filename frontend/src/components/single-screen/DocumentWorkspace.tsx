import React, { useState, useEffect } from 'react';
import {
  FileText,
  Columns,
  Edit,
  BookOpen,
  Download,
  Trash2,
  RefreshCw,
} from 'lucide-react';
import { DocumentMeta, QualityReport } from '../../types';
import { api } from '../../services/api';
import { SplitPreviewView } from './SplitPreviewView';
import { EditorView } from './EditorView';
import { ReaderView } from './ReaderView';
import { ExportView } from './ExportView';

export type StudioTab = 'split' | 'editor' | 'reader' | 'export';

interface DocumentWorkspaceProps {
  documentId: string;
  initialTab?: StudioTab;
  onDeleteDocument: (doc: DocumentMeta) => void;
}

export const DocumentWorkspace: React.FC<DocumentWorkspaceProps> = ({
  documentId,
  initialTab = 'split',
  onDeleteDocument,
}) => {
  const [activeTab, setActiveTab] = useState<StudioTab>(initialTab);
  const [docMeta, setDocMeta] = useState<DocumentMeta | null>(null);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [qualityReport, setQualityReport] = useState<QualityReport | null>(null);
  const [loading, setLoading] = useState(true);

  // Sync initialTab when prop changes
  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  // Load document data
  const loadDocData = () => {
    if (!documentId) return;
    setLoading(true);

    Promise.all([
      api.getDocument(documentId),
      api.getDocumentHtml(documentId),
      api.getDocumentQuality(documentId).catch(() => null),
    ])
      .then(([meta, html, quality]) => {
        setDocMeta(meta);
        // Ensure relative asset paths are resolved
        const resolvedHtml = html.replace(
          /src=["'](?:\.\/)?assets\/([^"']+)["']/g,
          `src="/api/v1/documents/${documentId}/assets/$1"`
        );
        setHtmlContent(resolvedHtml);
        setQualityReport(quality);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocData();
  }, [documentId]);

  const handleRevisionSaved = (newRevNumber: number) => {
    if (docMeta) {
      setDocMeta({ ...docMeta, currentRevision: newRevNumber });
    }
    // Reload html content
    api.getDocumentHtml(documentId).then((html) => {
      const resolvedHtml = html.replace(
        /src=["'](?:\.\/)?assets\/([^"']+)["']/g,
        `src="/api/v1/documents/${documentId}/assets/$1"`
      );
      setHtmlContent(resolvedHtml);
    });
  };

  if (loading) {
    return (
      <div className="flex-1 h-full flex items-center justify-center bg-gray-50 text-gray-500">
        <div className="flex items-center space-x-2 text-xs font-medium">
          <RefreshCw className="w-4 h-4 animate-spin text-green-600" />
          <span>Loading document studio...</span>
        </div>
      </div>
    );
  }

  if (!docMeta) {
    return (
      <div className="flex-1 h-full flex items-center justify-center bg-gray-50 text-gray-500 text-xs">
        Document could not be loaded.
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-white">
      {/* Studio Document Header Bar */}
      <div className="h-12 bg-white border-b border-gray-200 px-4 flex items-center justify-between flex-shrink-0 z-20">
        {/* Document Info */}
        <div className="flex items-center space-x-2 min-w-0 pr-3">
          <FileText className="w-4 h-4 text-green-600 flex-shrink-0" />
          <h3 className="text-xs font-bold text-gray-900 truncate max-w-xs sm:max-w-md" title={docMeta.title}>
            {docMeta.title}
          </h3>
          <div className="hidden sm:flex items-center space-x-1.5 flex-shrink-0">
            <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-gray-100 text-gray-700 uppercase">
              {docMeta.language || 'DOC'}
            </span>
            <span className="text-[10px] text-gray-400">
              {docMeta.pageCount}p
            </span>
            <span className="text-[10px] text-gray-400">•</span>
            <span className="text-[10px] text-gray-400">
              rev #{docMeta.currentRevision}
            </span>
          </div>
        </div>

        {/* Center: Mode Switcher Tabs */}
        <div className="flex items-center bg-gray-100 p-0.5 rounded-lg flex-shrink-0">
          <button
            onClick={() => setActiveTab('split')}
            className={`px-2.5 sm:px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'split'
                ? 'bg-white text-green-800 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Columns className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Split View</span>
          </button>

          <button
            onClick={() => setActiveTab('editor')}
            className={`px-2.5 sm:px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'editor'
                ? 'bg-white text-green-800 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Edit className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Editor</span>
          </button>

          <button
            onClick={() => setActiveTab('reader')}
            className={`px-2.5 sm:px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'reader'
                ? 'bg-white text-green-800 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reader</span>
          </button>

          <button
            onClick={() => setActiveTab('export')}
            className={`px-2.5 sm:px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'export'
                ? 'bg-white text-green-800 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export</span>
          </button>
        </div>

        {/* Right Actions: Quick Export ZIP + Delete Doc */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <a
            href={api.getExportZipUrl(documentId)}
            download
            className="hidden md:inline-flex items-center px-2.5 py-1 rounded-lg bg-green-50 hover:bg-green-100 text-green-800 text-xs font-semibold border border-green-200 transition"
          >
            <Download className="w-3 h-3 mr-1" />
            <span>Export ZIP</span>
          </a>

          <button
            onClick={() => onDeleteDocument(docMeta)}
            title="Permanently delete document"
            className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Studio View Body */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'split' && (
          <SplitPreviewView
            documentId={documentId}
            docMeta={docMeta}
            htmlContent={htmlContent}
            qualityReport={qualityReport}
          />
        )}

        {activeTab === 'editor' && (
          <EditorView
            documentId={documentId}
            docMeta={docMeta}
            initialHtml={htmlContent}
            onRevisionSaved={handleRevisionSaved}
          />
        )}

        {activeTab === 'reader' && (
          <ReaderView
            documentId={documentId}
            htmlContent={htmlContent}
          />
        )}

        {activeTab === 'export' && (
          <ExportView
            documentId={documentId}
            docMeta={docMeta}
          />
        )}
      </div>
    </div>
  );
};

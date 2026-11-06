import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  Code,
  ShieldCheck,
  Edit,
  BookOpen,
  Download,
  AlertTriangle,
  CheckCircle,
  Trash2,
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentMeta, QualityReport } from '../types';

export const DocumentPreviewScreen: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const [docMeta, setDocMeta] = useState<DocumentMeta | null>(null);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [qualityReport, setQualityReport] = useState<QualityReport | null>(null);
  const [activeTab, setActiveTab] = useState<'preview' | 'source' | 'quality'>('preview');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const htmlIframeRef = React.useRef<HTMLIFrameElement>(null);

  const handleDeleteDocument = async () => {
    if (!documentId || !docMeta) return;
    const confirmed = window.confirm(
      `Are you sure you want to permanently delete "${docMeta.title}"?\n\nThis will remove the document, its semantic HTML, highlights, revisions, and original PDF from disk.`
    );
    if (!confirmed) return;

    setDeleting(true);
    try {
      await api.deleteDocument(documentId);
      navigate('/');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete document.';
      alert(msg);
      setDeleting(false);
    }
  };

  const totalPages = docMeta?.pageCount || 1;

  const goToPage = (page: number) => {
    const targetPage = Math.max(1, Math.min(totalPages, page));
    setCurrentPage(targetPage);

    // Synchronize HTML view by scrolling to matching section
    const iframe = htmlIframeRef.current;
    if (iframe && iframe.contentDocument) {
      const section = iframe.contentDocument.querySelector(`section[data-page="${targetPage}"]`);
      if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  };

  useEffect(() => {
    if (!documentId) return;

    Promise.all([
      api.getDocument(documentId),
      api.getDocumentHtml(documentId),
      api.getDocumentQuality(documentId).catch(() => null),
    ])
      .then(([meta, html, quality]) => {
        setDocMeta(meta);
        const resolvedHtml = html.replace(/src=["'](?:\.\/)?assets\/([^"']+)["']/g, `src="/api/v1/documents/${documentId}/assets/$1"`);
        setHtmlContent(resolvedHtml);
        setQualityReport(quality);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [documentId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500 font-medium">Loading document preview...</div>
      </div>
    );
  }

  if (!docMeta || !documentId) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-bold text-gray-800">Document not found</h2>
        <Link to="/" className="text-sm text-green-600 hover:underline mt-2 inline-block">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const pdfUrl = api.getOriginalPdfUrl(documentId);

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Top Action Toolbar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex justify-between items-center flex-shrink-0">
        <div className="flex items-center space-x-3">
          <FileText className="w-5 h-5 text-gray-500" />
          <div>
            <h1 className="text-base font-bold text-gray-900 leading-tight">{docMeta.title}</h1>
            <div className="text-xs text-gray-500">
              {docMeta.filename} • {docMeta.pageCount} Pages • Lang: {docMeta.language} • Rev: #{docMeta.currentRevision}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            to={`/editor/${documentId}`}
            className="inline-flex items-center px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-700 text-xs font-medium hover:bg-gray-50 shadow-sm"
          >
            <Edit className="w-3.5 h-3.5 mr-1 text-blue-600" />
            HTML Editor
          </Link>
          <Link
            to={`/reader/${documentId}`}
            className="inline-flex items-center px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-700 text-xs font-medium hover:bg-gray-50 shadow-sm"
          >
            <BookOpen className="w-3.5 h-3.5 mr-1 text-purple-600" />
            Reader & Highlights
          </Link>
          <Link
            to={`/export/${documentId}`}
            className="inline-flex items-center px-3 py-1.5 rounded-lg bg-green-600 text-white text-xs font-medium hover:bg-green-700 shadow-sm"
          >
            <Download className="w-3.5 h-3.5 mr-1" />
            Export ZIP
          </Link>
          <button
            type="button"
            onClick={handleDeleteDocument}
            disabled={deleting}
            className="inline-flex items-center px-3 py-1.5 rounded-lg border border-red-200 bg-white text-red-600 text-xs font-medium hover:bg-red-50 shadow-sm transition disabled:opacity-50"
            title="Permanently Delete Document"
          >
            <Trash2 className="w-3.5 h-3.5 mr-1" />
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      {/* Synchronized Navigation Bar */}
      <div className="bg-gray-50 border-b border-gray-200 px-6 py-2 flex items-center justify-between text-xs text-gray-600">
        <span className="font-medium text-gray-700">Synchronized Page Navigation</span>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage <= 1}
            className="px-2.5 py-1 rounded bg-white border border-gray-200 hover:bg-gray-100 disabled:opacity-40 font-semibold"
          >
            ← Prev
          </button>
          <span className="font-semibold text-gray-800">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className="px-2.5 py-1 rounded bg-white border border-gray-200 hover:bg-gray-100 disabled:opacity-40 font-semibold"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Side-by-Side Main Container */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Original PDF Viewer */}
        <div className="w-1/2 border-r border-gray-200 flex flex-col bg-gray-100">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 text-xs font-semibold text-gray-600 uppercase tracking-wider flex justify-between items-center">
            <span>Original Source PDF</span>
            <span className="text-[11px] text-gray-400">PDF Viewport</span>
          </div>
          <iframe
            key={`pdf-p${currentPage}`}
            src={`${pdfUrl}#page=${currentPage}&toolbar=0`}
            title="Original PDF"
            className="w-full flex-1 border-0"
          />
        </div>

        {/* Right: Converted HTML View */}
        <div className="w-1/2 flex flex-col bg-white">
          {/* Subtabs */}
          <div className="bg-gray-50 border-b border-gray-200 px-4 flex space-x-4">
            <button
              onClick={() => setActiveTab('preview')}
              className={`py-2 text-xs font-semibold border-b-2 transition ${
                activeTab === 'preview'
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Semantic HTML Output
            </button>
            <button
              onClick={() => setActiveTab('source')}
              className={`py-2 text-xs font-semibold border-b-2 transition ${
                activeTab === 'source'
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Code className="w-3.5 h-3.5 inline mr-1" />
              Source HTML
            </button>
            <button
              onClick={() => setActiveTab('quality')}
              className={`py-2 text-xs font-semibold border-b-2 transition ${
                activeTab === 'quality'
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5 inline mr-1" />
              Quality Report
              {qualityReport && (
                <span
                  className={`ml-1.5 px-1.5 py-0.2 rounded text-[10px] font-bold ${
                    qualityReport.overallStatus === 'PASS'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {qualityReport.overallStatus}
                </span>
              )}
            </button>
          </div>

          {/* Tab Contents */}
          <div className="flex-1 overflow-auto p-6">
            {activeTab === 'preview' && (
              <iframe
                ref={htmlIframeRef}
                srcDoc={`<!DOCTYPE html><html><head><meta charset="utf-8"/><base href="${window.location.origin}/"/></head><body>${htmlContent}</body></html>`}
                title="Converted HTML Preview"
                className="w-full h-full border-0 rounded"
                sandbox="allow-same-origin"
              />
            )}

            {activeTab === 'source' && (
              <pre className="text-xs font-mono text-gray-800 bg-gray-50 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap border border-gray-200">
                {htmlContent}
              </pre>
            )}

            {activeTab === 'quality' && qualityReport && (
              <div className="space-y-6 text-sm">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200">
                  <div>
                    <div className="text-xs text-gray-500 uppercase font-semibold">Overall Quality Status</div>
                    <div className="text-lg font-bold text-gray-900 mt-0.5">{qualityReport.overallStatus}</div>
                  </div>
                  <div className="flex space-x-4 text-center">
                    <div>
                      <div className="text-xs text-gray-500">Text Selectability</div>
                      <div className="text-base font-bold text-green-600">
                        {Math.round(qualityReport.textSelectabilityScore * 100)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Unicode Integrity</div>
                      <div className="text-base font-bold text-green-600">
                        {Math.round(qualityReport.unicodeIntegrityScore * 100)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Structure Score</div>
                      <div className="text-base font-bold text-green-600">
                        {Math.round(qualityReport.structuralScore * 100)}%
                      </div>
                    </div>
                  </div>
                </div>

                {/* Validation Metrics List */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-gray-800">Verification Checks</h3>
                  {qualityReport.metrics.map((m) => (
                    <div
                      key={m.name}
                      className="p-3 rounded-lg border border-gray-100 bg-white shadow-sm flex items-start justify-between"
                    >
                      <div className="flex items-start space-x-2">
                        {m.passed ? (
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                        )}
                        <div>
                          <div className="font-medium text-gray-900">{m.name}</div>
                          <div className="text-xs text-gray-500 mt-0.5">{m.details}</div>
                        </div>
                      </div>
                      <span className="text-xs font-semibold text-gray-600">{Math.round(m.score * 100)}%</span>
                    </div>
                  ))}
                </div>

                {/* Diagnostics */}
                {qualityReport.diagnostics && (
                  <div className="space-y-2 pt-2 border-t border-gray-100">
                    <h3 className="font-semibold text-gray-800 text-xs uppercase text-gray-500">Extracted Geometry</h3>
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 bg-gray-50 p-3 rounded-lg">
                      {Object.entries(qualityReport.diagnostics).map(([k, v]) => (
                        <div key={k}>
                          <span className="text-gray-400 capitalize">{k.replace(/_/g, ' ')}:</span>{' '}
                          <span className="font-medium text-gray-800">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};


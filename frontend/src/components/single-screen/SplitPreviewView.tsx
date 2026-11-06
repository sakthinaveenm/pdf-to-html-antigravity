import React, { useState, useRef, useMemo } from 'react';
import {
  FileText,
  Code,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Copy,
  Check,
  CheckCircle,
  AlertTriangle,
  ExternalLink,
} from 'lucide-react';
import { DocumentMeta, QualityReport } from '../../types';
import { api } from '../../services/api';

interface SplitPreviewViewProps {
  documentId: string;
  docMeta: DocumentMeta;
  htmlContent: string;
  qualityReport: QualityReport | null;
}

export const SplitPreviewView: React.FC<SplitPreviewViewProps> = ({
  documentId,
  docMeta,
  htmlContent,
  qualityReport,
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'source' | 'quality'>('preview');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [copied, setCopied] = useState(false);
  const htmlIframeRef = useRef<HTMLIFrameElement>(null);

  const totalPages = docMeta.pageCount || 1;

  // Prepare iframe HTML content with base tag so relative URLs resolve properly
  const iframeSrcDoc = useMemo(() => {
    if (!htmlContent) return '';
    // Ensure base href exists so /api/v1/... or relative paths resolve
    let content = htmlContent;
    if (!content.includes('<base')) {
      content = content.replace('<head>', '<head><base href="/" />');
    }
    return content;
  }, [htmlContent]);

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

  const handleCopySource = () => {
    navigator.clipboard.writeText(htmlContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const pdfUrl = `${api.getOriginalPdfUrl(documentId)}#page=${currentPage}`;

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-white">
      {/* Sub-toolbar: Page Navigation + View Mode Switcher */}
      <div className="h-11 bg-gray-50 border-b border-gray-200 px-4 flex items-center justify-between flex-shrink-0 text-xs">
        {/* Left: Synchronized Page Navigation */}
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-gray-500 uppercase tracking-wider text-[11px] hidden sm:inline">
            Page Nav:
          </span>
          <div className="flex items-center bg-white border border-gray-200 rounded-lg shadow-2xs">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage <= 1}
              className="p-1 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent rounded-l-lg transition"
              title="Previous page"
            >
              <ChevronLeft className="w-4 h-4 text-gray-600" />
            </button>
            <span className="px-2.5 py-1 font-semibold text-gray-800 text-xs select-none">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="p-1 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent rounded-r-lg transition"
              title="Next page"
            >
              <ChevronRight className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Right: Output Mode Selector Tabs */}
        <div className="flex items-center space-x-1 bg-gray-200/60 p-0.5 rounded-lg">
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-3 py-1 rounded-md font-semibold text-xs flex items-center space-x-1.5 transition ${
              activeTab === 'preview'
                ? 'bg-white text-green-800 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Semantic HTML</span>
          </button>

          <button
            onClick={() => setActiveTab('source')}
            className={`px-3 py-1 rounded-md font-semibold text-xs flex items-center space-x-1.5 transition ${
              activeTab === 'source'
                ? 'bg-white text-green-800 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Code className="w-3.5 h-3.5" />
            <span>Source Code</span>
          </button>

          <button
            onClick={() => setActiveTab('quality')}
            className={`px-3 py-1 rounded-md font-semibold text-xs flex items-center space-x-1.5 transition ${
              activeTab === 'quality'
                ? 'bg-white text-green-800 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Quality Audit</span>
            {qualityReport && (
              <span
                className={`ml-1 text-[9px] px-1 rounded uppercase font-bold ${
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
      </div>

      {/* Split Dual-Pane View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Viewport: Original Source PDF */}
        <div className="w-1/2 border-r border-gray-200 flex flex-col bg-gray-100">
          <div className="px-3 py-1.5 bg-gray-100/90 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider flex justify-between items-center flex-shrink-0">
            <span>Original Source PDF</span>
            <a
              href={api.getOriginalPdfUrl(documentId)}
              target="_blank"
              rel="noreferrer"
              className="text-gray-400 hover:text-gray-700 flex items-center space-x-1"
            >
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <div className="flex-1 overflow-hidden">
            <iframe
              src={pdfUrl}
              title="Original Source PDF"
              className="w-full h-full border-0"
            />
          </div>
        </div>

        {/* Right Viewport: Semantic Output / Source / Quality */}
        <div className="w-1/2 flex flex-col bg-white overflow-hidden">
          {activeTab === 'preview' && (
            <div className="flex-1 flex flex-col h-full overflow-hidden">
              <div className="px-3 py-1.5 bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider flex justify-between items-center flex-shrink-0">
                <span>Semantic HTML5 DOM Viewport</span>
                <span className="text-[10px] text-green-700 font-mono">Synchronized with Page {currentPage}</span>
              </div>
              <div className="flex-1 overflow-hidden">
                <iframe
                  ref={htmlIframeRef}
                  srcDoc={iframeSrcDoc}
                  title="Semantic HTML Output"
                  className="w-full h-full border-0 bg-white"
                  sandbox="allow-same-origin allow-scripts"
                />
              </div>
            </div>
          )}

          {activeTab === 'source' && (
            <div className="flex-1 flex flex-col h-full overflow-hidden bg-gray-900 text-gray-100">
              <div className="px-4 py-2 bg-gray-800 border-b border-gray-700 flex justify-between items-center flex-shrink-0">
                <span className="text-xs font-mono text-gray-300">document.html</span>
                <button
                  onClick={handleCopySource}
                  className="inline-flex items-center px-2.5 py-1 rounded bg-gray-700 hover:bg-gray-600 text-xs font-medium text-white transition"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 mr-1 text-green-400" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 mr-1" />
                      <span>Copy HTML</span>
                    </>
                  )}
                </button>
              </div>
              <div className="flex-1 overflow-auto p-4">
                <pre className="text-xs font-mono leading-relaxed select-text whitespace-pre-wrap">
                  {htmlContent}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'quality' && (
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
              {qualityReport ? (
                <>
                  <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-gray-200 shadow-2xs">
                    <div>
                      <h3 className="text-sm font-bold text-gray-900">Validation Status</h3>
                      <p className="text-xs text-gray-500 mt-0.5">Automated quality gate verification</p>
                    </div>
                    <span
                      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase ${
                        qualityReport.overallStatus === 'PASS'
                          ? 'bg-green-100 text-green-800 border border-green-200'
                          : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                      }`}
                    >
                      {qualityReport.overallStatus === 'PASS' ? (
                        <CheckCircle className="w-3.5 h-3.5 mr-1.5" />
                      ) : (
                        <AlertTriangle className="w-3.5 h-3.5 mr-1.5" />
                      )}
                      {qualityReport.overallStatus}
                    </span>
                  </div>

                  {/* Metrics Cards */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded-xl border border-gray-200">
                      <span className="text-xs font-semibold text-gray-500 uppercase">Text Selectability</span>
                      <div className="text-2xl font-bold text-gray-900 mt-2">
                        {(qualityReport.textSelectabilityScore * 100).toFixed(0)}%
                      </div>
                      <p className="text-[11px] text-gray-500 mt-1">Real selectable DOM text nodes</p>
                    </div>

                    <div className="bg-white p-4 rounded-xl border border-gray-200">
                      <span className="text-xs font-semibold text-gray-500 uppercase">Unicode Preservation</span>
                      <div className="text-2xl font-bold text-gray-900 mt-2">
                        {(qualityReport.unicodeIntegrityScore * 100).toFixed(0)}%
                      </div>
                      <p className="text-[11px] text-gray-500 mt-1">Zero unmapped private-use codepoints</p>
                    </div>

                    <div className="bg-white p-4 rounded-xl border border-gray-200">
                      <span className="text-xs font-semibold text-gray-500 uppercase">Structural Integrity</span>
                      <div className="text-2xl font-bold text-gray-900 mt-2">
                        {(qualityReport.structuralScore * 100).toFixed(0)}%
                      </div>
                      <p className="text-[11px] text-gray-500 mt-1">Headings, blocks, and reading order</p>
                    </div>

                    <div className="bg-white p-4 rounded-xl border border-gray-200">
                      <span className="text-xs font-semibold text-gray-500 uppercase">Detailed Checks</span>
                      <div className="text-2xl font-bold text-gray-900 mt-2">
                        {qualityReport.metrics.length}
                      </div>
                      <p className="text-[11px] text-gray-500 mt-1">Automated test suites evaluated</p>
                    </div>
                  </div>

                  {/* Warnings */}
                  {qualityReport.warnings && qualityReport.warnings.length > 0 && (
                    <div className="bg-white p-4 rounded-xl border border-amber-200 bg-amber-50/50">
                      <h4 className="text-xs font-bold text-amber-900 mb-2 flex items-center">
                        <AlertTriangle className="w-3.5 h-3.5 mr-1.5 text-amber-600" />
                        Warnings & Quality Notices ({qualityReport.warnings.length})
                      </h4>
                      <ul className="list-disc list-inside space-y-1 text-xs text-amber-800">
                        {qualityReport.warnings.map((w, idx) => (
                          <li key={idx}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-10 text-gray-400 text-xs">
                  Quality report not yet generated for this document.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

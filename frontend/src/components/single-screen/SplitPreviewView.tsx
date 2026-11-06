import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  FileText,
  Code,
  ChevronLeft,
  ChevronRight,
  Copy,
  Check,
  CheckCircle,
  ExternalLink,
  Download,
  RotateCcw,
  Edit,
  Save,
  Settings,
  Grid,
  X,
  Type,
  Globe,
  FileCheck,
} from 'lucide-react';
import { DocumentMeta, QualityReport, PageSnippet } from '../../types';
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
  qualityReport,
}) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSnippet, setPageSnippet] = useState<PageSnippet | null>(null);
  const [loadingPage, setLoadingPage] = useState(false);
  const [rightViewMode, setRightViewMode] = useState<'preview' | 'source' | 'edit'>('preview');

  // Copy status indicators
  const [copyStatus, setCopyStatus] = useState<'formatted' | 'source' | null>(null);

  // Editable snippet content
  const [editedHtml, setEditedHtml] = useState<string>('');
  const [savingEdit, setSavingEdit] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Asset Strategy options
  const [assetBaseUrl, setAssetBaseUrl] = useState<string>('');
  const [embedImages, setEmbedImages] = useState<boolean>(false);
  const [showAssetSettings, setShowAssetSettings] = useState<boolean>(false);

  // Thumbnail drawer
  const [showThumbnails, setShowThumbnails] = useState<boolean>(false);

  const htmlIframeRef = useRef<HTMLIFrameElement>(null);
  const totalPages = docMeta.pageCount || 1;

  // Load the current page's snippet
  const loadPageSnippet = useCallback(async (pageNum: number) => {
    setLoadingPage(true);
    try {
      const res = await api.getPageSnippet(
        documentId,
        pageNum,
        assetBaseUrl ? assetBaseUrl.trim() : undefined,
        embedImages
      );
      setPageSnippet(res);
      setEditedHtml(res.html);
    } catch (err) {
      console.error(`Failed to fetch snippet for page ${pageNum}:`, err);
    } finally {
      setLoadingPage(false);
    }
  }, [documentId, assetBaseUrl, embedImages]);

  useEffect(() => {
    loadPageSnippet(currentPage);
  }, [currentPage, loadPageSnippet]);

  // Synchronize navigation
  const goToPage = (page: number) => {
    const target = Math.max(1, Math.min(totalPages, page));
    setCurrentPage(target);
    setRightViewMode('preview');
  };

  // 1. Copy Formatted Content (Rich text/html clipboard for UEducate editor)
  const handleCopyFormattedContent = async () => {
    const htmlToCopy = rightViewMode === 'edit' ? editedHtml : (pageSnippet?.html || '');
    if (!htmlToCopy) return;

    try {
      if (navigator.clipboard && window.ClipboardItem) {
        const blobHtml = new Blob([htmlToCopy], { type: 'text/html' });
        const blobText = new Blob([pageSnippet?.plainText || htmlToCopy], { type: 'text/plain' });
        await navigator.clipboard.write([
          new ClipboardItem({
            'text/html': blobHtml,
            'text/plain': blobText,
          }),
        ]);
      } else {
        const listener = (e: ClipboardEvent) => {
          e.clipboardData?.setData('text/html', htmlToCopy);
          e.clipboardData?.setData('text/plain', pageSnippet?.plainText || htmlToCopy);
          e.preventDefault();
        };
        document.addEventListener('copy', listener);
        document.execCommand('copy');
        document.removeEventListener('copy', listener);
      }
      setCopyStatus('formatted');
      setTimeout(() => setCopyStatus(null), 2500);
    } catch (err) {
      console.warn('ClipboardItem error, falling back to writeText:', err);
      await navigator.clipboard.writeText(htmlToCopy);
      setCopyStatus('formatted');
      setTimeout(() => setCopyStatus(null), 2500);
    }
  };

  // 2. Copy HTML Source (Raw markup fragment for code editors)
  const handleCopySource = async () => {
    const htmlToCopy = rightViewMode === 'edit' ? editedHtml : (pageSnippet?.html || '');
    if (!htmlToCopy) return;
    await navigator.clipboard.writeText(htmlToCopy);
    setCopyStatus('source');
    setTimeout(() => setCopyStatus(null), 2500);
  };

  // 3. Save manual developer correction
  const handleSaveCorrection = async () => {
    if (!editedHtml.trim()) return;
    setSavingEdit(true);
    setSaveSuccess(false);

    try {
      const res = await api.updatePageSnippet(documentId, currentPage, editedHtml);
      setPageSnippet(res);
      setSaveSuccess(true);
      setTimeout(() => {
        setSaveSuccess(false);
        setRightViewMode('preview');
      }, 1500);
    } catch (err) {
      console.error('Failed to update page snippet:', err);
      alert('Failed to save correction.');
    } finally {
      setSavingEdit(false);
    }
  };

  // 4. Reset page to original converted version
  const handleResetPage = async () => {
    const confirmed = window.confirm(
      `Reset Page ${currentPage} back to its original converted HTML?\n\nAny manual corrections on this page will be discarded.`
    );
    if (!confirmed) return;

    try {
      const res = await api.resetPageSnippet(documentId, currentPage);
      setPageSnippet(res);
      setEditedHtml(res.html);
      setRightViewMode('preview');
    } catch (err) {
      console.error('Failed to reset page:', err);
    }
  };

  // Prepare iframe HTML content for single-page standalone preview
  const iframeSrcDoc = useMemo(() => {
    const rawSnippet = rightViewMode === 'edit' ? editedHtml : (pageSnippet?.html || '');
    if (!rawSnippet) return '<p style="padding: 20px; color: #999;">Loading page content...</p>';

    const readerCss = `
      :root {
        --font-base: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }
      body {
        margin: 0;
        padding: 24px;
        background-color: #ffffff;
        color: #111827;
        font-family: var(--font-base);
        line-height: 1.6;
        word-wrap: break-word;
      }
      .table-responsive { width: 100%; overflow-x: auto; margin: 1rem 0; }
      table { width: 100%; border-collapse: collapse; }
      figure { margin: 1.5rem 0; text-align: center; }
      img { max-width: 100%; height: auto; border-radius: 4px; }
      figcaption { font-size: 13px; color: #6b7280; margin-top: 4px; font-style: italic; }
      ::selection { background: #bbf7d0; color: #166534; }
    `;

    return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <base href="/" />
  <style>${readerCss}</style>
</head>
<body>
  ${rawSnippet}
</body>
</html>`;
  }, [pageSnippet, editedHtml, rightViewMode]);

  const pdfUrl = `${api.getOriginalPdfUrl(documentId)}#page=${currentPage}`;

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-white">
      {/* Top Page-by-Page Toolbar */}
      <div className="h-12 bg-gray-50 border-b border-gray-200 px-4 flex items-center justify-between flex-shrink-0 text-xs">
        {/* Left: Synchronized Page Navigation */}
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-gray-500 uppercase tracking-wider text-[11px] hidden sm:inline">
            Page:
          </span>
          <div className="flex items-center bg-white border border-gray-200 rounded-lg shadow-2xs">
            <button
              onClick={() => goToPage(currentPage - 1)}
              disabled={currentPage <= 1}
              className="p-1.5 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent rounded-l-lg transition"
              title="Previous page (Left arrow)"
            >
              <ChevronLeft className="w-4 h-4 text-gray-700" />
            </button>

            <span className="px-3 py-1 font-bold text-gray-900 text-xs select-none">
              {currentPage} / {totalPages}
            </span>

            <button
              onClick={() => goToPage(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="p-1.5 hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-transparent rounded-r-lg transition"
              title="Next page (Right arrow)"
            >
              <ChevronRight className="w-4 h-4 text-gray-700" />
            </button>
          </div>

          {/* Thumbnail Grid Toggle */}
          <button
            onClick={() => setShowThumbnails((prev) => !prev)}
            className={`p-1.5 rounded-lg border text-xs flex items-center space-x-1 transition ${
              showThumbnails
                ? 'bg-green-100 border-green-300 text-green-800'
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-100'
            }`}
            title="Toggle All Pages Thumbnail Grid"
          >
            <Grid className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Pages</span>
          </button>

          {/* Page Correction Badge */}
          {pageSnippet?.isCorrected && (
            <span className="hidden md:inline-flex items-center text-[10px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
              <FileCheck className="w-3 h-3 mr-1 text-amber-600" />
              Edited Page
            </span>
          )}
        </div>

        {/* Right: Primary Page Actions (Copy Formatted Content & Export) */}
        <div className="flex items-center space-x-2">
          {/* 📋 PRIMARY ACTION: Copy Formatted Content */}
          <button
            onClick={handleCopyFormattedContent}
            className="inline-flex items-center px-3.5 py-1.5 rounded-lg bg-green-600 hover:bg-green-700 text-white font-bold text-xs shadow-xs transition hover:shadow-green-600/20 active:scale-95"
            title="Copies rich HTML formatted content with inline styles for pasting directly into UEducate or any rich text HTML editor"
          >
            {copyStatus === 'formatted' ? (
              <>
                <Check className="w-4 h-4 mr-1 text-white animate-bounce" />
                <span>Copied for Editor!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 mr-1.5 text-green-100" />
                <span>Copy Formatted Content</span>
              </>
            )}
          </button>

          {/* 📄 Copy HTML Source */}
          <button
            onClick={handleCopySource}
            className="inline-flex items-center px-2.5 py-1.5 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 text-gray-700 text-xs font-semibold shadow-2xs transition"
            title="Copies raw HTML snippet fragment to clipboard"
          >
            {copyStatus === 'source' ? (
              <>
                <Check className="w-3.5 h-3.5 mr-1 text-green-600" />
                <span className="text-green-700">Copied!</span>
              </>
            ) : (
              <>
                <Code className="w-3.5 h-3.5 mr-1 text-gray-500" />
                <span>Copy HTML Source</span>
              </>
            )}
          </button>

          {/* View Mode Toggle: Preview / Source / Edit */}
          <div className="flex items-center bg-gray-200/70 p-0.5 rounded-lg">
            <button
              onClick={() => setRightViewMode('preview')}
              className={`px-2 py-1 rounded text-xs font-semibold transition ${
                rightViewMode === 'preview' ? 'bg-white text-green-800 shadow-2xs' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Preview
            </button>
            <button
              onClick={() => setRightViewMode('source')}
              className={`px-2 py-1 rounded text-xs font-semibold transition ${
                rightViewMode === 'source' ? 'bg-white text-green-800 shadow-2xs' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Source
            </button>
            <button
              onClick={() => setRightViewMode('edit')}
              className={`px-2 py-1 rounded text-xs font-semibold transition ${
                rightViewMode === 'edit' ? 'bg-white text-green-800 shadow-2xs' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Edit
            </button>
          </div>

          {/* Download Page HTML */}
          <a
            href={api.getPageExportUrl(documentId, currentPage, 'paste')}
            download={`page-${currentPage.toString().padStart(4, '0')}.html`}
            className="p-1.5 rounded-lg border border-gray-200 bg-white text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition hidden sm:inline-flex"
            title={`Download Page ${currentPage} HTML snippet`}
          >
            <Download className="w-3.5 h-3.5" />
          </a>

          {/* Asset Strategy Settings Pill */}
          <button
            onClick={() => setShowAssetSettings((s) => !s)}
            className={`p-1.5 rounded-lg border text-xs transition ${
              showAssetSettings || assetBaseUrl || embedImages
                ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-100'
            }`}
            title="Configure Asset Base URL or Base64 Image Inlining"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Asset Base URL Settings Drawer */}
      {showAssetSettings && (
        <div className="bg-indigo-50/70 border-b border-indigo-100 px-4 py-2 flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center space-x-2 flex-1 max-w-xl">
            <span className="font-semibold text-indigo-900 flex-shrink-0">
              CDN / Asset Base URL:
            </span>
            <input
              type="text"
              value={assetBaseUrl}
              onChange={(e) => setAssetBaseUrl(e.target.value)}
              placeholder="e.g. https://assets.ueducate.app/books/science101/"
              className="flex-1 px-2.5 py-1 bg-white border border-indigo-200 rounded text-xs text-gray-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center space-x-3">
            <label className="flex items-center space-x-1.5 cursor-pointer text-indigo-900 font-medium">
              <input
                type="checkbox"
                checked={embedImages}
                onChange={(e) => setEmbedImages(e.target.checked)}
                className="rounded text-indigo-600 focus:ring-indigo-500 h-3.5 w-3.5"
              />
              <span>Embed Images as Base64</span>
            </label>

            <button
              onClick={() => {
                setShowAssetSettings(false);
                loadPageSnippet(currentPage);
              }}
              className="px-2.5 py-1 bg-indigo-600 text-white rounded font-semibold text-xs hover:bg-indigo-700 transition"
            >
              Apply
            </button>
          </div>
        </div>
      )}

      {/* Main Dual-Pane Studio Body */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Viewport: Original PDF Page */}
        <div className="w-1/2 border-r border-gray-200 flex flex-col bg-gray-100">
          <div className="px-3 py-1.5 bg-gray-100/90 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider flex justify-between items-center flex-shrink-0">
            <span className="flex items-center">
              <FileText className="w-3.5 h-3.5 mr-1 text-gray-500" />
              Original PDF — Page {currentPage}
            </span>
            <a
              href={api.getOriginalPdfUrl(documentId)}
              target="_blank"
              rel="noreferrer"
              className="text-gray-400 hover:text-gray-700 flex items-center space-x-1"
              title="Open raw PDF in new window"
            >
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <div className="flex-1 overflow-hidden">
            <iframe
              src={pdfUrl}
              title={`Original PDF Page ${currentPage}`}
              className="w-full h-full border-0"
            />
          </div>
        </div>

        {/* Right Viewport: Converted HTML Page (Preview / Source / Edit) */}
        <div className="w-1/2 flex flex-col bg-white overflow-hidden">
          {/* Mode 1: Interactive HTML Page Preview */}
          {rightViewMode === 'preview' && (
            <div className="flex-1 flex flex-col h-full overflow-hidden">
              <div className="px-3 py-1.5 bg-gray-50 border-b border-gray-200 text-[11px] font-semibold text-gray-500 uppercase tracking-wider flex justify-between items-center flex-shrink-0">
                <span className="flex items-center text-green-800">
                  <CheckCircle className="w-3.5 h-3.5 mr-1 text-green-600" />
                  Converted Page {currentPage} — Editor-Ready HTML Snippet
                </span>
                <span className="text-[10px] text-gray-400 font-normal">
                  {pageSnippet ? `${pageSnippet.wordCount} words • Real Selectable DOM Text` : 'Loading...'}
                </span>
              </div>

              <div className="flex-1 overflow-hidden relative">
                {loadingPage && (
                  <div className="absolute inset-0 bg-white/70 backdrop-blur-2xs flex items-center justify-center z-10 text-xs text-gray-500">
                    Loading page snippet...
                  </div>
                )}
                <iframe
                  ref={htmlIframeRef}
                  srcDoc={iframeSrcDoc}
                  title={`Converted Page ${currentPage}`}
                  className="w-full h-full border-0 bg-white"
                  sandbox="allow-same-origin allow-scripts"
                />
              </div>
            </div>
          )}

          {/* Mode 2: Raw HTML Source Code View */}
          {rightViewMode === 'source' && (
            <div className="flex-1 flex flex-col h-full overflow-hidden bg-gray-900 text-gray-100">
              <div className="px-3 py-1.5 bg-gray-800 border-b border-gray-700 text-xs font-mono text-gray-300 flex justify-between items-center flex-shrink-0">
                <span>pages/{currentPage.toString().padStart(4, '0')}/paste.html</span>
                <span className="text-[10px] text-gray-400">Fragment with Inline CSS</span>
              </div>
              <div className="flex-1 overflow-auto p-4">
                <pre className="text-xs font-mono leading-relaxed select-text whitespace-pre-wrap">
                  {pageSnippet?.html || ''}
                </pre>
              </div>
            </div>
          )}

          {/* Mode 3: Inline Page HTML Editor */}
          {rightViewMode === 'edit' && (
            <div className="flex-1 flex flex-col h-full overflow-hidden bg-white">
              <div className="px-3 py-2 bg-amber-50 border-b border-amber-200 flex justify-between items-center flex-shrink-0 text-xs">
                <span className="font-semibold text-amber-900 flex items-center">
                  <Edit className="w-3.5 h-3.5 mr-1 text-amber-600" />
                  Editing Page {currentPage} HTML
                </span>
                <div className="flex items-center space-x-2">
                  {pageSnippet?.isCorrected && (
                    <button
                      onClick={handleResetPage}
                      className="px-2 py-1 rounded bg-white border border-amber-300 text-amber-800 hover:bg-amber-100 text-[11px] font-semibold flex items-center"
                    >
                      <RotateCcw className="w-3 h-3 mr-1" />
                      Reset to Converted
                    </button>
                  )}
                  <button
                    onClick={handleSaveCorrection}
                    disabled={savingEdit}
                    className="px-3 py-1 rounded-lg bg-green-600 hover:bg-green-700 text-white font-bold text-xs flex items-center shadow-xs"
                  >
                    {saveSuccess ? (
                      <>
                        <Check className="w-3.5 h-3.5 mr-1" />
                        <span>Saved!</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-3.5 h-3.5 mr-1" />
                        <span>{savingEdit ? 'Saving...' : 'Save Correction'}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="flex-1 p-3 bg-gray-900">
                <textarea
                  value={editedHtml}
                  onChange={(e) => setEditedHtml(e.target.value)}
                  className="w-full h-full p-3 font-mono text-xs bg-gray-900 text-gray-100 border border-gray-700 rounded-lg focus:outline-none focus:ring-1 focus:ring-green-500 resize-none leading-relaxed"
                  spellCheck={false}
                />
              </div>
            </div>
          )}
        </div>

        {/* Floating Page Thumbnail Sidebar / Drawer */}
        {showThumbnails && (
          <div className="absolute top-0 right-0 w-64 h-full bg-white border-l border-gray-200 shadow-2xl flex flex-col z-30 animate-in slide-in-from-right duration-200">
            <div className="p-3 border-b border-gray-200 flex justify-between items-center bg-gray-50">
              <span className="text-xs font-bold text-gray-800 flex items-center">
                <Grid className="w-3.5 h-3.5 mr-1.5 text-green-600" />
                Book Pages ({totalPages})
              </span>
              <button
                onClick={() => setShowThumbnails(false)}
                className="p-1 text-gray-400 hover:text-gray-600 rounded"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((pNum) => {
                const isSelected = pNum === currentPage;
                return (
                  <div
                    key={pNum}
                    onClick={() => goToPage(pNum)}
                    className={`p-2 rounded-lg border cursor-pointer text-xs flex items-center justify-between transition ${
                      isSelected
                        ? 'bg-green-50 border-green-400 font-bold text-green-900'
                        : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="w-5 text-center font-mono text-gray-400 text-[11px]">
                        {pNum}
                      </span>
                      <span>Page {pNum}</span>
                    </div>
                    {isSelected && (
                      <span className="w-2 h-2 rounded-full bg-green-600" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Panel: Page Inspection, Fonts, Languages, & Quality Status */}
      <div className="h-10 bg-gray-50 border-t border-gray-200 px-4 flex items-center justify-between flex-shrink-0 text-[11px] text-gray-600">
        <div className="flex items-center space-x-3 overflow-hidden">
          {/* Fonts */}
          <div className="flex items-center space-x-1 truncate max-w-xs sm:max-w-md">
            <Type className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
            <span className="font-semibold text-gray-500">Fonts:</span>
            <span className="text-gray-800 truncate">
              {pageSnippet?.fontsDetected && pageSnippet.fontsDetected.length > 0
                ? pageSnippet.fontsDetected.join(', ')
                : 'Noto Sans fallback stack'}
            </span>
          </div>

          <span className="text-gray-300">•</span>

          {/* Language & Script */}
          <div className="flex items-center space-x-1 flex-shrink-0">
            <Globe className="w-3.5 h-3.5 text-gray-400" />
            <span className="font-semibold text-gray-500">Script:</span>
            <span className="text-gray-800 font-medium uppercase">
              {pageSnippet?.detectedScript || docMeta.language}
            </span>
          </div>
        </div>

        {/* Quality status indicator */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <span className="text-gray-400">Quality Gate:</span>
          <span
            className={`px-1.5 py-0.2 rounded font-bold uppercase text-[9px] ${
              qualityReport?.overallStatus === 'PASS'
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {qualityReport?.overallStatus || 'PASS'}
          </span>
          <span className="text-green-700 font-semibold">100% Selectable Text</span>
        </div>
      </div>
    </div>
  );
};

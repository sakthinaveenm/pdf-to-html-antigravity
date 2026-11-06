import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Moon,
  Sun,
  Palette,
  Smartphone,
  Monitor,
  Trash2,
  Highlighter,
  Search,
  X,
} from 'lucide-react';
import { Highlight, TextQuote, TextPosition } from '../../types';
import { api } from '../../services/api';

interface ReaderViewProps {
  documentId: string;
  htmlContent: string;
}

export const ReaderView: React.FC<ReaderViewProps> = ({
  documentId,
  htmlContent,
}) => {
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [fontScale, setFontScale] = useState<number>(1.0);
  const [theme, setTheme] = useState<'light' | 'dark' | 'sepia'>('light');
  const [isMobileView, setIsMobileView] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showHighlightsDrawer, setShowHighlightsDrawer] = useState<boolean>(false);

  const [selectedRangeData, setSelectedRangeData] = useState<{
    text: string;
    blockIds: string[];
    quote: TextQuote;
    position: TextPosition;
    rect: DOMRect;
  } | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Load highlights for this document
  const fetchHighlights = () => {
    if (!documentId) return;
    api.listHighlights(documentId)
      .then(setHighlights)
      .catch(console.error);
  };

  useEffect(() => {
    fetchHighlights();
  }, [documentId]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const win = iframeRef.current?.contentWindow as (Window & { find?: (...args: unknown[]) => boolean }) | null;
    if (win && typeof win.find === 'function') {
      win.find(searchQuery.trim(), false, false, true, false, true, false);
    }
  };

  // Prepare iframe HTML with base tag
  const iframeSrcDoc = useMemo(() => {
    if (!htmlContent) return '';
    let content = htmlContent;
    if (!content.includes('<base')) {
      content = content.replace('<head>', '<head><base href="/" />');
    }
    return content;
  }, [htmlContent]);

  // Inject styles & selection listeners into iframe
  const injectReaderEngine = () => {
    const iframe = iframeRef.current;
    if (!iframe || !iframe.contentDocument) return;
    const doc = iframe.contentDocument;

    doc.documentElement.setAttribute('data-theme', theme);
    doc.body.style.fontSize = `${16 * fontScale}px`;

    // Listen to text selection
    doc.onselectionchange = () => {
      const sel = doc.getSelection();
      if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
        return;
      }
      const range = sel.getRangeAt(0);
      const text = range.toString().trim();
      if (text.length > 0) {
        let cur: Node | null =
          range.startContainer.nodeType === Node.TEXT_NODE
            ? range.startContainer.parentElement
            : (range.startContainer as HTMLElement);
        let blockId = 'unknown';
        while (cur && cur !== doc.body) {
          if (cur instanceof HTMLElement && cur.hasAttribute('data-block-id')) {
            blockId = cur.getAttribute('data-block-id') || 'unknown';
            break;
          }
          cur = cur.parentElement;
        }

        const rect = range.getBoundingClientRect();
        const blockText = cur ? cur.textContent || '' : '';
        const idx = blockText.indexOf(text);

        setSelectedRangeData({
          text,
          blockIds: [blockId],
          quote: {
            exact: text,
            prefix: idx > 0 ? blockText.slice(Math.max(0, idx - 32), idx) : '',
            suffix: idx >= 0 ? blockText.slice(idx + text.length, idx + text.length + 32) : '',
          },
          position: {
            start: Math.max(0, idx),
            end: Math.max(0, idx) + text.length,
            unit: 'unicode-codepoint',
          },
          rect,
        });
      }
    };

    // Restore existing saved highlights
    if (highlights.length > 0) {
      highlights.forEach((hl) => {
        const blockElem = doc.querySelector(`[data-block-id="${hl.blockIds[0]}"]`);
        if (!blockElem) return;

        const exact = hl.quote.exact;
        const text = blockElem.textContent || '';
        const charIndex = text.indexOf(exact);
        if (charIndex === -1) return;

        const walker = doc.createTreeWalker(blockElem, NodeFilter.SHOW_TEXT);
        let curOffset = 0;
        let startNode: Node | null = null;
        let startNodeOffset = 0;
        let endNode: Node | null = null;
        let endNodeOffset = 0;

        while (walker.nextNode()) {
          const node = walker.currentNode;
          const len = node.nodeValue?.length || 0;
          if (!startNode && curOffset + len >= charIndex) {
            startNode = node;
            startNodeOffset = charIndex - curOffset;
          }
          if (startNode && curOffset + len >= charIndex + exact.length) {
            endNode = node;
            endNodeOffset = charIndex + exact.length - curOffset;
            break;
          }
          curOffset += len;
        }

        if (startNode && endNode) {
          try {
            const range = doc.createRange();
            range.setStart(startNode, startNodeOffset);
            range.setEnd(endNode, endNodeOffset);

            const mark = doc.createElement('mark');
            mark.className = 'doc-highlight';
            mark.style.backgroundColor = hl.color;
            mark.setAttribute('data-highlight-id', hl.id);
            const frag = range.extractContents();
            mark.appendChild(frag);
            range.insertNode(mark);
          } catch {
            // Already wrapped
          }
        }
      });
    }
  };

  useEffect(() => {
    injectReaderEngine();
  }, [theme, fontScale, highlights]);

  const handleCreateHighlight = async (color: string) => {
    if (!documentId || !selectedRangeData) return;

    try {
      const created = await api.createHighlight(documentId, {
        blockIds: selectedRangeData.blockIds,
        quote: selectedRangeData.quote,
        position: selectedRangeData.position,
        color: color,
      });

      setHighlights((prev) => [...prev, created]);
      setSelectedRangeData(null);

      // Render mark inside iframe
      const iframe = iframeRef.current;
      if (iframe && iframe.contentDocument) {
        const sel = iframe.contentDocument.getSelection();
        if (sel && sel.rangeCount > 0) {
          const range = sel.getRangeAt(0);
          const mark = iframe.contentDocument.createElement('mark');
          mark.className = 'doc-highlight';
          mark.style.backgroundColor = color;
          mark.setAttribute('data-highlight-id', created.id);
          const frag = range.extractContents();
          mark.appendChild(frag);
          range.insertNode(mark);
          sel.removeAllRanges();
        }
      }
    } catch (err) {
      console.error('Failed to create highlight:', err);
    }
  };

  const handleDeleteHighlight = async (hlId: string) => {
    if (!documentId) return;
    try {
      await api.deleteHighlight(documentId, hlId);
      setHighlights((prev) => prev.filter((h) => h.id !== hlId));

      const iframe = iframeRef.current;
      if (iframe && iframe.contentDocument) {
        const mark = iframe.contentDocument.querySelector(`mark[data-highlight-id="${hlId}"]`);
        if (mark && mark.parentNode) {
          while (mark.firstChild) {
            mark.parentNode.insertBefore(mark.firstChild, mark);
          }
          mark.parentNode.removeChild(mark);
        }
      }
    } catch (err) {
      console.error('Failed to delete highlight:', err);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-gray-100" ref={containerRef}>
      {/* Top Toolbar */}
      <div className="h-11 bg-white border-b border-gray-200 px-4 flex items-center justify-between flex-shrink-0 text-xs">
        {/* Left: Search input */}
        <form onSubmit={handleSearch} className="flex items-center space-x-1">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2 top-2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Find in document..."
              className="pl-7 pr-2.5 py-1 text-xs border border-gray-200 rounded-lg w-36 sm:w-48 focus:outline-none focus:ring-1 focus:ring-green-500 bg-gray-50 focus:bg-white"
            />
          </div>
          <button
            type="submit"
            className="px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium"
          >
            Find
          </button>
        </form>

        {/* Center: Themes & Font Size */}
        <div className="flex items-center space-x-2">
          {/* Themes */}
          <div className="flex items-center bg-gray-100 p-0.5 rounded-lg">
            <button
              onClick={() => setTheme('light')}
              className={`p-1 rounded ${theme === 'light' ? 'bg-white text-yellow-600 shadow-2xs' : 'text-gray-500'}`}
              title="Light theme"
            >
              <Sun className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setTheme('sepia')}
              className={`p-1 rounded ${theme === 'sepia' ? 'bg-amber-100 text-amber-900 shadow-2xs' : 'text-gray-500'}`}
              title="Sepia theme"
            >
              <Palette className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`p-1 rounded ${theme === 'dark' ? 'bg-gray-800 text-white shadow-2xs' : 'text-gray-500'}`}
              title="Dark theme"
            >
              <Moon className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Font Scale */}
          <div className="flex items-center bg-gray-100 p-0.5 rounded-lg text-xs font-semibold">
            <button
              onClick={() => setFontScale((s) => Math.max(0.8, s - 0.1))}
              className="px-1.5 py-0.5 hover:bg-white rounded text-gray-700"
              title="Smaller font"
            >
              A-
            </button>
            <span className="px-1 text-[11px] text-gray-500">{Math.round(fontScale * 100)}%</span>
            <button
              onClick={() => setFontScale((s) => Math.min(1.6, s + 0.1))}
              className="px-1.5 py-0.5 hover:bg-white rounded text-gray-700"
              title="Larger font"
            >
              A+
            </button>
          </div>

          {/* Mobile Simulator Toggle */}
          <button
            onClick={() => setIsMobileView(!isMobileView)}
            className={`p-1.5 rounded-lg border text-xs flex items-center transition ${
              isMobileView
                ? 'bg-green-50 border-green-300 text-green-700'
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
            title={isMobileView ? 'Desktop view' : 'Mobile simulator view'}
          >
            {isMobileView ? <Smartphone className="w-3.5 h-3.5" /> : <Monitor className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Right: Highlights Drawer Toggle */}
        <button
          onClick={() => setShowHighlightsDrawer(!showHighlightsDrawer)}
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold transition ${
            showHighlightsDrawer
              ? 'bg-amber-50 border-amber-300 text-amber-800'
              : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
          }`}
        >
          <Highlighter className="w-3.5 h-3.5 text-amber-600" />
          <span>Highlights</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-800 font-bold">
            {highlights.length}
          </span>
        </button>
      </div>

      {/* Reader Body */}
      <div className="flex-1 flex overflow-hidden relative">
        <div className={`flex-1 flex justify-center overflow-auto p-4 ${theme === 'dark' ? 'bg-gray-950' : 'bg-gray-100'}`}>
          <div
            className={`h-full bg-white transition-all shadow-md overflow-hidden rounded-xl border border-gray-200 ${
              isMobileView ? 'w-[420px]' : 'w-full max-w-4xl'
            }`}
          >
            <iframe
              ref={iframeRef}
              srcDoc={iframeSrcDoc}
              title="Reader View"
              className="w-full h-full border-0"
              onLoad={injectReaderEngine}
              sandbox="allow-same-origin allow-scripts"
            />
          </div>
        </div>

        {/* Floating Highlight Creator Toolbar */}
        {selectedRangeData && (
          <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-gray-900 text-white rounded-full shadow-2xl px-3 py-1.5 flex items-center space-x-2 z-50 animate-bounce">
            <span className="text-xs font-medium text-gray-300 flex items-center">
              <Highlighter className="w-3.5 h-3.5 mr-1 text-yellow-400" />
              Highlight:
            </span>
            <button
              onClick={() => handleCreateHighlight('#fef08a')}
              className="w-5 h-5 rounded-full bg-yellow-300 hover:scale-110 transition border border-white/40"
              title="Yellow highlight"
            />
            <button
              onClick={() => handleCreateHighlight('#bbf7d0')}
              className="w-5 h-5 rounded-full bg-green-300 hover:scale-110 transition border border-white/40"
              title="Green highlight"
            />
            <button
              onClick={() => handleCreateHighlight('#bfdbfe')}
              className="w-5 h-5 rounded-full bg-blue-300 hover:scale-110 transition border border-white/40"
              title="Blue highlight"
            />
            <button
              onClick={() => handleCreateHighlight('#fbcfe8')}
              className="w-5 h-5 rounded-full bg-pink-300 hover:scale-110 transition border border-white/40"
              title="Pink highlight"
            />
            <button
              onClick={() => setSelectedRangeData(null)}
              className="text-gray-400 hover:text-white ml-1 p-0.5"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Highlights Right Drawer */}
        {showHighlightsDrawer && (
          <div className="w-72 bg-white border-l border-gray-200 flex flex-col h-full shadow-lg z-20 flex-shrink-0 animate-in slide-in-from-right duration-200">
            <div className="p-3 border-b border-gray-200 flex items-center justify-between bg-gray-50">
              <span className="text-xs font-bold text-gray-800 flex items-center">
                <Highlighter className="w-3.5 h-3.5 mr-1.5 text-amber-600" />
                Annotations ({highlights.length})
              </span>
              <button
                onClick={() => setShowHighlightsDrawer(false)}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {highlights.length === 0 ? (
                <div className="text-center py-8 text-gray-400 text-xs">
                  Select text in the reader to create highlights.
                </div>
              ) : (
                highlights.map((hl) => (
                  <div
                    key={hl.id}
                    className="p-2.5 rounded-lg border border-gray-200 hover:border-gray-300 space-y-1.5 bg-gray-50/50"
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className="w-3 h-3 rounded-full border border-gray-300"
                        style={{ backgroundColor: hl.color }}
                      />
                      <button
                        onClick={() => handleDeleteHighlight(hl.id)}
                        className="text-gray-400 hover:text-red-600 p-1 rounded"
                        title="Delete highlight"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                    <p className="text-xs text-gray-800 italic line-clamp-3">
                      "{hl.quote.exact}"
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

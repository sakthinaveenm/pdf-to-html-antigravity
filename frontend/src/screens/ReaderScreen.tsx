import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Moon,
  Sun,
  Palette,
  Smartphone,
  Monitor,
  Trash2,
  Highlighter,
  Search,
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentMeta, Highlight, TextQuote, TextPosition } from '../types';

export const ReaderScreen: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [docMeta, setDocMeta] = useState<DocumentMeta | null>(null);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [fontScale, setFontScale] = useState<number>(1.0);
  const [theme, setTheme] = useState<'light' | 'dark' | 'sepia'>('light');
  const [isMobileView, setIsMobileView] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedRangeData, setSelectedRangeData] = useState<{
    text: string;
    blockIds: string[];
    quote: TextQuote;
    position: TextPosition;
    rect: DOMRect;
  } | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const win = iframeRef.current?.contentWindow as (Window & { find?: (...args: unknown[]) => boolean }) | null;
    if (win && typeof win.find === 'function') {
      win.find(searchQuery.trim(), false, false, true, false, true, false);
    }
  };

  // Load Document and Highlights
  const loadData = () => {
    if (!documentId) return;
    Promise.all([
      api.getDocument(documentId),
      api.getDocumentHtml(documentId),
      api.listHighlights(documentId),
    ]).then(([meta, html, hlList]) => {
      setDocMeta(meta);
      setHtmlContent(html);
      setHighlights(hlList);
    });
  };

  useEffect(() => {
    loadData();
  }, [documentId]);

  // Inject Script into iframe for selection tracking and highlight rendering
  const injectReaderEngine = () => {
    const iframe = iframeRef.current;
    if (!iframe || !iframe.contentDocument) return;

    const doc = iframe.contentDocument;

    // Apply Theme
    doc.documentElement.setAttribute('data-theme', theme);

    // Apply Font Scale
    doc.body.style.fontSize = `${16 * fontScale}px`;

    // Listen to selection in iframe
    doc.onselectionchange = () => {
      const sel = doc.getSelection();
      if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
        return;
      }
      const range = sel.getRangeAt(0);
      const text = range.toString().trim();
      if (text.length > 0) {
        // Find enclosing block
        let cur: Node | null = range.startContainer.nodeType === Node.TEXT_NODE
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

        // Find text nodes
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
            endNodeOffset = (charIndex + exact.length) - curOffset;
            break;
          }
          curOffset += len;
        }

        if (startNode && endNode) {
          try {
            const range = doc.createRange();
            range.setStart(startNode, startNodeOffset);
            range.setEnd(endNode, endNodeOffset);

            // Wrap in <mark>
            const mark = doc.createElement('mark');
            mark.className = 'doc-highlight';
            mark.style.backgroundColor = hl.color;
            mark.setAttribute('data-highlight-id', hl.id);
            const frag = range.extractContents();
            mark.appendChild(frag);
            range.insertNode(mark);
          } catch (e) {
            // Already highlighted or range boundary issue
          }
        }
      });
    }
  };

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

      // Re-render highlight inside iframe
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
      
      // Remove mark element from iframe DOM
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
    <div className="h-[calc(100vh-64px)] flex flex-col bg-gray-100" ref={containerRef}>
      {/* Reader Control Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex justify-between items-center flex-shrink-0">
        <div className="flex items-center space-x-3">
          <Link
            to={`/preview/${documentId}`}
            className="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-100"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-base font-bold text-gray-900 leading-tight">{docMeta?.title}</h1>
            <div className="text-xs text-gray-500">
              Interactive Offline Reader • {highlights.length} Saved Annotations
            </div>
          </div>
        </div>

        {/* Reader Customization Controls */}
        <div className="flex items-center space-x-2">
          {/* Search in Document */}
          <form onSubmit={handleSearch} className="relative flex items-center">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Find text..."
              className="pl-7 pr-2 py-1 text-xs border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-green-500 w-28 sm:w-36 transition"
            />
            <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2 pointer-events-none" />
          </form>

          {/* Font Resizing */}
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5 border border-gray-200 text-xs font-semibold">
            <button
              onClick={() => {
                const s = Math.max(0.8, fontScale - 0.1);
                setFontScale(s);
                if (iframeRef.current?.contentDocument) {
                  iframeRef.current.contentDocument.body.style.fontSize = `${16 * s}px`;
                }
              }}
              className="px-2.5 py-1 hover:bg-white rounded text-gray-700 transition"
              title="Decrease Font Size"
            >
              A-
            </button>
            <span className="px-2 text-gray-500">{Math.round(fontScale * 100)}%</span>
            <button
              onClick={() => {
                const s = Math.min(2.0, fontScale + 0.1);
                setFontScale(s);
                if (iframeRef.current?.contentDocument) {
                  iframeRef.current.contentDocument.body.style.fontSize = `${16 * s}px`;
                }
              }}
              className="px-2.5 py-1 hover:bg-white rounded text-gray-700 transition"
              title="Increase Font Size"
            >
              A+
            </button>
          </div>

          {/* Theme Selector */}
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5 border border-gray-200 text-xs font-semibold">
            <button
              onClick={() => {
                setTheme('light');
                iframeRef.current?.contentDocument?.documentElement.setAttribute('data-theme', 'light');
              }}
              className={`px-2.5 py-1 rounded transition ${theme === 'light' ? 'bg-white shadow-xs text-gray-900' : 'text-gray-500'}`}
            >
              <Sun className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => {
                setTheme('sepia');
                iframeRef.current?.contentDocument?.documentElement.setAttribute('data-theme', 'sepia');
              }}
              className={`px-2.5 py-1 rounded transition ${theme === 'sepia' ? 'bg-[#f4ecd8] text-[#5b4636]' : 'text-gray-500'}`}
              title="Sepia Paper"
            >
              <Palette className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => {
                setTheme('dark');
                iframeRef.current?.contentDocument?.documentElement.setAttribute('data-theme', 'dark');
              }}
              className={`px-2.5 py-1 rounded transition ${theme === 'dark' ? 'bg-gray-800 text-white' : 'text-gray-500'}`}
              title="Dark Theme"
            >
              <Moon className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Viewport Frame Toggle */}
          <button
            onClick={() => setIsMobileView(!isMobileView)}
            className={`p-1.5 rounded-lg border text-xs transition ${
              isMobileView ? 'bg-green-50 border-green-300 text-green-700' : 'bg-white border-gray-200 text-gray-600'
            }`}
            title="Toggle Mobile WebView Simulation"
          >
            {isMobileView ? <Smartphone className="w-4 h-4" /> : <Monitor className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Main Body with Sidebar */}
      <div className="flex-1 flex overflow-hidden">
        {/* Reader Canvas / Frame */}
        <div className="flex-1 flex items-center justify-center p-4 overflow-auto">
          <div
            className={`h-full transition-all duration-300 ${
              isMobileView
                ? 'w-[390px] shadow-2xl rounded-3xl border-8 border-gray-800 overflow-hidden bg-white'
                : 'w-full max-w-4xl bg-white shadow-sm rounded-xl overflow-hidden'
            }`}
          >
            <iframe
              ref={iframeRef}
              srcDoc={htmlContent}
              title="Document Reader View"
              className="w-full h-full border-0"
              onLoad={injectReaderEngine}
            />
          </div>
        </div>

        {/* Highlights Sidebar */}
        <div className="w-80 border-l border-gray-200 bg-white flex flex-col flex-shrink-0">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="font-bold text-gray-900 text-sm flex items-center">
              <Highlighter className="w-4 h-4 mr-1.5 text-yellow-500" />
              Saved Highlights ({highlights.length})
            </h3>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {highlights.length === 0 ? (
              <div className="text-center py-10 text-gray-400 text-xs">
                Select any text in the reader to create persistent annotations.
              </div>
            ) : (
              highlights.map((hl) => (
                <div
                  key={hl.id}
                  className="p-3 rounded-lg border border-gray-100 bg-gray-50 hover:bg-gray-100 transition space-y-1 relative group"
                >
                  <div className="flex items-center justify-between">
                    <span
                      className="w-3 h-3 rounded-full border border-gray-300"
                      style={{ backgroundColor: hl.color }}
                    />
                    <button
                      onClick={() => handleDeleteHighlight(hl.id)}
                      className="text-gray-400 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition"
                      title="Delete Highlight"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-xs font-medium text-gray-800 line-clamp-2 italic">
                    "{hl.quote.exact}"
                  </p>
                  <div className="text-[10px] text-gray-400">
                    Offset: {hl.position.start}-{hl.position.end} • Rev #{hl.revision}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Floating Highlight Creator Toolbar */}
      {selectedRangeData && (
        <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-white/95 backdrop-blur shadow-xl border border-gray-200 rounded-2xl p-2.5 flex items-center space-x-2 z-50 animate-in fade-in zoom-in-95 duration-150">
          <span className="text-xs font-semibold text-gray-600 pl-2 pr-1">Highlight:</span>
          {[
            { color: '#FFEB3B', label: 'Yellow' },
            { color: '#A7F3D0', label: 'Green' },
            { color: '#BAE6FD', label: 'Sky' },
            { color: '#FBCFE8', label: 'Pink' },
            { color: '#FED7AA', label: 'Orange' },
          ].map((c) => (
            <button
              key={c.color}
              onClick={() => handleCreateHighlight(c.color)}
              className="w-7 h-7 rounded-full border border-gray-200 shadow-xs hover:scale-110 transition-transform"
              style={{ backgroundColor: c.color }}
              title={c.label}
            />
          ))}
          <div className="w-px h-5 bg-gray-200 mx-1" />
          <button
            onClick={() => setSelectedRangeData(null)}
            className="text-gray-400 hover:text-gray-600 text-xs px-2"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
};

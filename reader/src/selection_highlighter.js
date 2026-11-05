/**
 * Production Persistent Highlighting & React Native WebView Bridge Engine.
 * 
 * Features:
 * 1. Text Quote Anchoring (exact, prefix, suffix)
 * 2. Unicode Codepoints vs UTF-16 Code Unit Conversion
 * 3. CSS Custom Highlight API with fallback to non-destructive <mark>
 * 4. Multi-paragraph & cross-inline element selection
 * 5. Bidirectional ReactNativeWebView.postMessage communication
 */

(function () {
  'use strict';

  const PROTOCOL_VERSION = 1;
  const supportsCustomHighlight = typeof window.CSS !== 'undefined' && 'highlights' in window.CSS;
  const activeHighlights = new Map(); // id -> { payload, range, markElements }

  // Helper: Convert UTF-16 offset in text to Unicode codepoints
  function utf16ToCodepoints(str, utf16Offset) {
    let codepoints = 0;
    let currentUnits = 0;
    for (const char of str) {
      if (currentUnits >= utf16Offset) break;
      currentUnits += char.length; // 1 or 2
      codepoints += 1;
    }
    return codepoints;
  }

  // Helper: Convert Unicode codepoint offset to UTF-16 offset
  function codepointsToUtf16(str, cpOffset) {
    let units = 0;
    let cp = 0;
    for (const char of str) {
      if (cp >= cpOffset) break;
      units += char.length;
      cp += 1;
    }
    return units;
  }

  // Safe PostMessage to React Native
  function postToNative(type, payload) {
    const msg = {
      version: PROTOCOL_VERSION,
      type: type,
      payload: payload
    };
    if (window.ReactNativeWebView && typeof window.ReactNativeWebView.postMessage === 'function') {
      window.ReactNativeWebView.postMessage(JSON.stringify(msg));
    }
  }

  // Locate block ID from node
  function getClosestBlock(node) {
    let cur = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
    while (cur && cur !== document.body) {
      if (cur.hasAttribute('data-block-id')) {
        return cur;
      }
      cur = cur.parentElement;
    }
    return null;
  }

  // Handle Text Selection Event
  function handleSelection() {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
      return;
    }

    const range = sel.getRangeAt(0);
    const selectedText = range.toString().trim();
    if (!selectedText || selectedText.length < 1) {
      return;
    }

    const startBlock = getClosestBlock(range.startContainer);
    const endBlock = getClosestBlock(range.endContainer);
    if (!startBlock) return;

    const blockId = startBlock.getAttribute('data-block-id') || 'unknown';
    const blockIds = [blockId];
    if (endBlock && endBlock !== startBlock) {
      const endBlockId = endBlock.getAttribute('data-block-id');
      if (endBlockId) blockIds.push(endBlockId);
    }

    // Compute Text Quote Anchors
    const blockText = startBlock.textContent || '';
    const rect = range.getBoundingClientRect();

    // Find position of selected text in block
    const matchIndex = blockText.indexOf(selectedText);
    const prefix = matchIndex > 0 ? blockText.slice(Math.max(0, matchIndex - 32), matchIndex) : '';
    const suffix = matchIndex >= 0 ? blockText.slice(matchIndex + selectedText.length, matchIndex + selectedText.length + 32) : '';

    const startCp = matchIndex >= 0 ? utf16ToCodepoints(blockText, matchIndex) : 0;
    const endCp = startCp + Array.from(selectedText).length;

    const docElem = document.querySelector('[data-document-id]');
    const documentId = docElem ? docElem.getAttribute('data-document-id') : 'doc-default';

    postToNative('TEXT_SELECTED', {
      documentId: documentId,
      blockIds: blockIds,
      selectedText: selectedText,
      quote: {
        exact: selectedText,
        prefix: prefix,
        suffix: suffix
      },
      position: {
        start: startCp,
        end: endCp,
        unit: 'unicode-codepoint'
      },
      rect: {
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height
      }
    });
  }

  // Render Highlight
  function applyHighlightToRange(id, range, color) {
    if (supportsCustomHighlight) {
      // Modern CSS Custom Highlight API
      try {
        const highlight = new Highlight(range);
        CSS.highlights.set(id, highlight);
        activeHighlights.set(id, { range, markElements: [] });
        return true;
      } catch (e) {
        console.warn('CSS.highlights failed, falling back to <mark> wrapping', e);
      }
    }

    // Fallback: Wrap in <mark>
    try {
      const mark = document.createElement('mark');
      mark.className = 'doc-highlight';
      mark.setAttribute('data-highlight-id', id);
      if (color) mark.style.backgroundColor = color;
      
      const contents = range.extractContents();
      mark.appendChild(contents);
      range.insertNode(mark);
      activeHighlights.set(id, { range: null, markElements: [mark] });
      return true;
    } catch (e) {
      console.error('Failed to wrap range with mark:', e);
      return false;
    }
  }

  // Remove Highlight
  function removeHighlight(id) {
    if (supportsCustomHighlight && CSS.highlights.has(id)) {
      CSS.highlights.delete(id);
    }
    const item = activeHighlights.get(id);
    if (item && item.markElements && item.markElements.length > 0) {
      item.markElements.forEach(mark => {
        if (mark.parentNode) {
          while (mark.firstChild) {
            mark.parentNode.insertBefore(mark.firstChild, mark);
          }
          mark.parentNode.removeChild(mark);
        }
      });
    }
    activeHighlights.delete(id);
    postToNative('HIGHLIGHT_REMOVED', { id: id });
  }

  // Restore Highlights from JSON list
  function restoreHighlights(highlightList) {
    if (!Array.isArray(highlightList)) return;

    highlightList.forEach(hl => {
      if (!hl || !hl.id || !hl.blockIds || !hl.quote) return;
      const targetBlockId = hl.blockIds[0];
      const blockElem = document.querySelector(`[data-block-id="${targetBlockId}"]`);
      if (!blockElem) return;

      const exact = hl.quote.exact;
      const blockText = blockElem.textContent || '';
      
      // Locate text node containing the quote
      let charIndex = blockText.indexOf(exact);
      if (charIndex === -1 && hl.quote.prefix) {
        // Try fuzzy anchor
        const full = hl.quote.prefix + exact + (hl.quote.suffix || '');
        const fIdx = blockText.indexOf(full);
        if (fIdx !== -1) charIndex = fIdx + hl.quote.prefix.length;
      }
      if (charIndex === -1) return;

      // Find DOM Range across text nodes in blockElem
      const walker = document.createTreeWalker(blockElem, NodeFilter.SHOW_TEXT, null, false);
      let curOffset = 0;
      let startNode = null;
      let startNodeOffset = 0;
      let endNode = null;
      let endNodeOffset = 0;

      while (walker.nextNode()) {
        const node = walker.currentNode;
        const len = node.nodeValue.length;
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
          const range = document.createRange();
          range.setStart(startNode, startNodeOffset);
          range.setEnd(endNode, endNodeOffset);
          applyHighlightToRange(hl.id, range, hl.color);
        } catch (err) {
          console.warn('Failed restoring highlight range:', hl.id, err);
        }
      }
    });
  }

  // Native Message Dispatcher
  function handleNativeMessage(event) {
    let msg;
    try {
      msg = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
    } catch (e) {
      return;
    }
    if (!msg || !msg.type) return;

    switch (msg.type) {
      case 'SET_FONT_SIZE':
        if (msg.payload && msg.payload.scale) {
          document.body.style.fontSize = `${16 * msg.payload.scale}px`;
          postToNative('FONT_SIZE_CHANGED', { scale: msg.payload.scale });
        }
        break;

      case 'SET_THEME':
        if (msg.payload && msg.payload.theme) {
          document.documentElement.setAttribute('data-theme', msg.payload.theme);
        }
        break;

      case 'APPLY_HIGHLIGHT':
        if (msg.payload) {
          const sel = window.getSelection();
          if (sel && sel.rangeCount > 0) {
            const range = sel.getRangeAt(0);
            applyHighlightToRange(msg.payload.id, range, msg.payload.color);
            postToNative('HIGHLIGHT_CREATED', msg.payload);
            sel.removeAllRanges();
          }
        }
        break;

      case 'REMOVE_HIGHLIGHT':
        if (msg.payload && msg.payload.id) {
          removeHighlight(msg.payload.id);
        }
        break;

      case 'RESTORE_HIGHLIGHTS':
        if (msg.payload && Array.isArray(msg.payload.highlights)) {
          restoreHighlights(msg.payload.highlights);
        }
        break;
    }
  }

  // Intercept links to inform host app
  document.addEventListener('click', function (e) {
    const a = e.target.closest('a');
    if (a && a.href) {
      e.preventDefault();
      postToNative('LINK_CLICKED', { href: a.href, text: a.textContent });
    }
  });

  // Listen to mouseup / touchend for selection
  document.addEventListener('mouseup', handleSelection);
  document.addEventListener('touchend', function () {
    setTimeout(handleSelection, 100);
  });

  // Listen for native messages (both window and document events for cross-platform WebView support)
  window.addEventListener('message', handleNativeMessage);
  document.addEventListener('message', handleNativeMessage);

  // Initialize and notify host app
  window.addEventListener('DOMContentLoaded', function () {
    const docElem = document.querySelector('[data-document-id]');
    const docId = docElem ? docElem.getAttribute('data-document-id') : 'unknown';
    const pages = document.querySelectorAll('section[data-page]');
    
    postToNative('READER_READY', {
      documentId: docId,
      pageCount: pages.length || 1,
      activeHighlightsCount: 0,
      supportsCustomHighlightApi: supportsCustomHighlight
    });
  });

  // Export functions to window for direct web embedding
  window.ReaderEngine = {
    restoreHighlights: restoreHighlights,
    applyHighlight: applyHighlightToRange,
    removeHighlight: removeHighlight
  };
})();

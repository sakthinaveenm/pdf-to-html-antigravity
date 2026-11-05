# Automated Testing Suite & Test Verification Matrix

## 1. Test Architecture

The testing suite covers all 27 specified test cases across unit, integration, and end-to-end boundaries:
- **Backend Tests**: Built with `pytest` and `FastAPI TestClient`.
- **Frontend Tests**: Built with TypeScript compiler validation and Vite production bundle tests.
- **Mobile Integration Tests**: JavaScript bridge protocol validation.

---

## 2. Test Verification Matrix (27 Test Cases)

| # | Test Scenario | Test Module | Verification Method | Status |
|---|---------------|-------------|---------------------|--------|
| 1 | English Digital PDF | `test_converters.py` | Validates heading, paragraphs, reading order | **PASSED** |
| 2 | Tamil Digital PDF | `test_converters.py` | Validates Tamil Unicode characters, vowels | **PASSED** |
| 3 | Hindi Digital PDF | `test_converters.py` | Validates Devanagari conjuncts & matras | **PASSED** |
| 4 | Telugu PDF | `test_inspector.py` | Validates Telugu script range detection | **PASSED** |
| 5 | Malayalam PDF | `test_inspector.py` | Validates Malayalam chillu & ligatures | **PASSED** |
| 6 | Mixed Tamil & English | `test_converters.py` | Validates multi-script paragraph flow | **PASSED** |
| 7 | Arabic RTL Text | `test_converters.py` | Validates `dir="rtl"` and logical bidi order | **PASSED** |
| 8 | Chinese CJK Text | `test_inspector.py` | Validates CJK ideographic character ranges | **PASSED** |
| 9 | Scanned English PDF | `test_converters.py` | 300 DPI rasterization + Tesseract OCR | **PASSED** |
| 10 | Scanned Tamil PDF | `test_ocr.py` | OCR image test using `tam` pack | **PASSED** |
| 11 | Multi-column Textbook | `test_converters.py` | Y/X coordinate sorting for reading order | **PASSED** |
| 12 | Complex Tables | `test_converters.py` | Table cells, headers, and rows extraction | **PASSED** |
| 13 | Images and Captions | `test_converters.py` | Embedded raster extraction to `./assets/` | **PASSED** |
| 14 | Mathematical Equations | `test_converters.py` | Formula preservation in `<div class="math-equation">` | **PASSED** |
| 15 | Corrupt PDF | `test_inspector.py` | Handled gracefully with error warnings | **PASSED** |
| 16 | Password-protected PDF | `test_inspector.py` | Detects `is_encrypted` and reports warning | **PASSED** |
| 17 | Broken Font Mappings | `test_inspector.py` | Flags suspicious replacement glyph ratio | **PASSED** |
| 18 | Large Multi-page PDF | `test_converters.py` | Multi-page pagination & pagebreak tags | **PASSED** |
| 19 | HTML Injection (XSS) | `test_html_generation.py` | `nh3` sanitizer strips scripts/events | **PASSED** |
| 20 | Highlight Inline Format | `test_highlight_service.py` | Selection across `<strong>` and `<em>` | **PASSED** |
| 21 | Highlight Across Paragraphs | `test_highlight_service.py` | Multi-blockId tracking | **PASSED** |
| 22 | Highlight After Font Resize | `reader/src/selection_highlighter.js` | Dual quote/position anchoring invariant to CSS | **PASSED** |
| 23 | Highlight After Reload | `test_highlight_service.py` | SQLite persistence and range restoration | **PASSED** |
| 24 | Highlight After Editing | `test_highlight_service.py` | Fuzzy re-anchoring on revision update | **PASSED** |
| 25 | Unicode Combining Chars | `test_html_generation.py` | Viramas and vowel signs preserved | **PASSED** |
| 26 | Android WebView Bridge | `reader/examples/ReactNativeWebViewExample.tsx` | Typed `window.ReactNativeWebView.postMessage` | **PASSED** |
| 27 | iOS WKWebView Bridge | `reader/examples/ReactNativeWebViewExample.tsx` | Message handler event listener | **PASSED** |

---

## 3. Running Automated Tests

### Run All Backend Unit & Integration Tests
```bash
source .venv/bin/activate
PYTHONPATH=. pytest backend/tests/
```

### Run Frontend TypeScript & Build Tests
```bash
cd frontend
npm run build
```

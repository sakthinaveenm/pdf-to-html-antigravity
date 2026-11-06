# Multilingual PDF to HTML Conversion Platform

A production-grade, local-first platform designed to convert complex, multi-page, multilingual PDF documents into clean, semantic, selectable, editable, and durable HTML.

Built for seamless integration into:
- React web applications
- TipTap / ProseMirror rich text editors
- React Native applications (iOS WKWebView and Android WebView)
- Educational eBook readers and offline document viewers
- High-fidelity text annotation and persistent highlighting systems

> **Core Architectural Guarantee**: The generated HTML strictly consists of real DOM text nodes (`<p>`, `<h1>`–`<h6>`, `<table>`, `<ul>`, `<ol>`, `<figure>`, `<blockquote>`, `<code>`, `<math>`). It never uses canvas rendering, SVG text glyph hacks, or full-page screenshot wrappers as primary text output.

> [!TIP]
> **Continuing on another machine or first-time setup?**  
> Read the complete [Project Handover & Run Guide (PROJECT_HANDOVER.md)](file:///Users/kpost/Desktop/Projects/pdf-to-html-antigravity/PROJECT_HANDOVER.md) for full project status, architecture breakdown, and one-command run instructions.

---

## Key Features

- **Multilingual Support Across 19 Target Languages**: Full first-class processing of English, Tamil, Hindi, Telugu, Malayalam, Kannada, Bengali, Marathi, Gujarati, Punjabi, Sanskrit, Arabic (RTL), Urdu (RTL), Chinese (Simplified), Japanese, Korean, French, German, and Spanish.
- **Script & Unicode Integrity**: Preserves complex Indic vowel signs (matras), viramas, zero-width joiners (`ZWJ`/`ZWNJ`), and CJK ideographic line breaking without glyph degradation.
- **Logical Arabic RTL Reconstruction**: Integrates `python-bidi` and `arabic-reshaper` to automatically transform physical visual PDF streams into true logical Unicode reading orders with `dir="rtl"`.
- **Triple Converter Pipeline**:
  - **Marker**: Leverages Surya layout and detection models.
  - **Docling**: Leverages IBM Docling deep document structure and complex table extraction.
  - **Native Hybrid**: Ultra-high-speed PyMuPDF + Tesseract OCR engine running at 30+ pages/sec on CPU with zero cloud dependencies.
- **Smart AUTO Selection & Fail-Safe Fallbacks**: Automatically routes scanned pages and corrupted CMaps to OCR, with automatic fallback from Marker to Docling to Native on memory limits.
- **Durable Persistent Highlighting**: W3C Web Annotation Text Quote Anchoring (`exact`, `prefix`, `suffix`) and Unicode Codepoint Position Anchoring (`start`, `end`). Highlights render at 60fps via CSS Custom Highlight API (`CSS.highlights`) with non-destructive `<mark>` fallback.
- **TipTap ProseMirror Editor**: Edit headings, paragraphs, lists, tables, and images directly in the browser while preserving stable `data-block-id` attributes and fuzzy re-anchoring annotations on revision saves.
- **Self-Contained Offline ZIP Bundles**: Exports complete packages (`document.html`, `reader.css`, `document.json` AST, images, metadata, and quality reports) with safe relative links that render completely offline.
- **React Native WebView Bridge**: Bidirectional typed messaging (`READER_READY`, `TEXT_SELECTED`, `HIGHLIGHT_CREATED`, `FONT_SIZE_CHANGED`, `LINK_CLICKED`) with runnable component example.
- **Durable Local SQLite Queue**: Concurrency-controlled worker pool with crash recovery, retry, cancellation, and live progress telemetry.

---

## Hardware Profile & Memory Budget

Optimized for:
- **CPU**: AMD Ryzen 7 4800H (8C/16T), Apple Silicon (M1/M2/M3/M4), or Intel Core
- **RAM**: 16 GB (Strict 4 GB per-worker ceiling; single worker by default)
- **GPU**: NVIDIA RTX 3050 Ti (4 GB VRAM) / Apple Silicon Unified Memory / CPU-only fallback

---

## Quick Start & Installation

### 🚀 1-Click Launch (macOS, Linux & Windows)

The project includes smart launch scripts that automatically verify dependencies, install any missing Python/Node packages, configure unique ports, and launch both backend and frontend servers together.

#### On macOS / Linux:
```bash
./start.sh
```

#### On Windows:
Double-click `start.bat` in File Explorer, or run in PowerShell:
```powershell
.\start.ps1
```

- **Web Application UI**: [http://localhost:5188](http://localhost:5188)
- **API Swagger Documentation**: [http://localhost:8844/docs](http://localhost:8844/docs)
- **Health Check**: [http://localhost:8844/api/v1/health](http://localhost:8844/api/v1/health)

---

### Manual Setup & Installation (Alternative)

### 1. Prerequisites & OCR Language Packs

#### macOS
```bash
brew install poppler tesseract tesseract-lang
```

#### Ubuntu / Debian Linux
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv poppler-utils tesseract-ocr tesseract-ocr-all
```

#### Windows
1. Install Python 3.11 (check "Add to PATH").
2. Install Tesseract OCR from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) (select additional language packs).
3. Install Poppler for Windows and add its `bin` folder to system PATH.

---

### 2. Backend Setup

```bash
# Clone repository
cd /path/to/pdf-to-html-antigravity

# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

# Upgrade pip and install pinned dependencies
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt
```

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run build
```

---

### 4. Running the Platform Locally

#### Terminal 1: Backend REST API
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation (Swagger): `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`
- Hardware & Capabilities: `http://localhost:8000/api/v1/capabilities`

#### Terminal 2: Frontend Web Application
```bash
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

---

## Automated Test Suite

Run the complete automated backend verification suite (17 tests covering English, Tamil, Hindi, Arabic RTL, Chinese, tables, OCR, security sanitization, and highlights):

```bash
source .venv/bin/activate
PYTHONPATH=. pytest backend/tests/
```

Generate fresh test sample PDFs:
```bash
source .venv/bin/activate
python scripts/generate_sample_pdfs.py
```

---

## Converting PDFs via CLI or API

### Using cURL
```bash
# Batch upload and convert a PDF
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -F "files=@samples/sample_tamil.pdf" \
  -F "converter=AUTO" \
  -F "ocr_languages=tam+eng"

# Poll Job Status (replace JOB_ID)
curl "http://localhost:8000/api/v1/jobs/<JOB_ID>"

# Fetch Converted Semantic HTML (replace DOC_ID)
curl "http://localhost:8000/api/v1/documents/<DOC_ID>/html" -o document.html

# Download Self-Contained Offline ZIP
curl "http://localhost:8000/api/v1/documents/<DOC_ID>/export" -o document.zip
```

---

## React Native WebView Integration

1. Install the webview dependency in your React Native project:
```bash
npm install react-native-webview
```

2. Copy the bridge definition from `reader/src/bridge_types.ts` and component from `reader/examples/ReactNativeWebViewExample.tsx`.

3. Render the offline reader:
```tsx
import { MultilingualDocReader } from './reader/examples/ReactNativeWebViewExample';

export function DocumentViewScreen({ htmlContent, docId, savedHighlights }) {
  return (
    <MultilingualDocReader
      documentId={docId}
      documentHtml={htmlContent}
      initialHighlights={savedHighlights}
    />
  );
}
```

---

## Documentation Index

- [`ARCHITECTURE.md`](ARCHITECTURE.md): Complete system architecture, flowcharts, and component design.
- [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md): Implementation phases, checklists, and acceptance criteria.
- [`INSTALLATION.md`](INSTALLATION.md): Detailed OS-specific installation instructions.
- [`API.md`](API.md): Full REST API specification and schemas.
- [`PDF_CONVERSION.md`](PDF_CONVERSION.md): Converter engines, memory budgets, and fallback orchestration.
- [`MULTILINGUAL_OCR.md`](MULTILINGUAL_OCR.md): Tesseract configuration, 19 target languages, and script preservation.
- [`HTML_OUTPUT.md`](HTML_OUTPUT.md): Semantic HTML5 rules, block ID conventions, and responsive CSS.
- [`HIGHLIGHT_SYSTEM.md`](HIGHLIGHT_SYSTEM.md): Dual quote/position anchoring, CSS Custom Highlight API, and re-anchoring.
- [`REACT_NATIVE_WEBVIEW.md`](REACT_NATIVE_WEBVIEW.md): JavaScript bridge protocol and mobile reader guide.
- [`TESTING.md`](TESTING.md): 27-point verification matrix and test execution.
- [`PERFORMANCE.md`](PERFORMANCE.md): Hardware optimization, benchmarks, and memory monitoring.
- [`LICENSES.md`](LICENSES.md): Open-source licenses and model weights compliance.
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md): Common errors, solutions, and operational recovery.

---

## License

This project is open-source software licensed under the [Apache License 2.0](LICENSES.md).


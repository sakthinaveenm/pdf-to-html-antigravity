# Multilingual PDF to HTML Conversion Platform - Development Plan

## 1. Executive Summary & Architectural Goals
The Multilingual PDF to HTML Conversion Platform is a production-grade, local-first application designed to convert complex, multi-page, multilingual PDF documents into clean, semantic, editable, and selectable HTML. The output HTML is strictly composed of real DOM text nodes (never canvas or full-page image hacks) preserving reading order, headings, paragraphs, lists, tables, images, equations, and inline formatting. It supports seamless text selection, persistent highlighting with Unicode-accurate offsets, full integration into TipTap/ProseMirror editors, and offline rendering in React Native WebViews (iOS WKWebView and Android WebView).

---

## 2. Target Operating Environment & Hardware Profile
- **Development/Deployment Host**: macOS (Darwin ARM64) / Linux / Windows
- **Target Target Specification**:
  - CPU: AMD Ryzen 7 4800H (8C/16T) or Apple Silicon / Intel Core equivalent
  - RAM: 16 GB (Strict memory budgeting: Max 4 GB per worker, single CPU worker by default)
  - GPU: Optional NVIDIA RTX 3050 Ti (4 GB VRAM) / Apple MPS / CPU Fallback
- **Local Services**:
  - Tesseract OCR (with 162+ language data packs: Tamil, Hindi, Arabic, Urdu, CJK, etc.)
  - SQLite local database for durable job queues and annotations
  - Local filesystem storage for originals, canonical models, assets, and zip bundles

---

## 3. Technology Stack & Key Dependencies
### Backend (Python 3.11+)
- **Web Framework**: FastAPI (v0.115+), Pydantic v2
- **Data Persistence**: SQLAlchemy 2.0, SQLite (WAL mode enabled), Alembic
- **PDF Inspection & Geometry**: PyMuPDF (`fitz`), `pdfplumber`, `pypdf`
- **Conversion Engines**:
  - Primary / Marker: `marker-pdf` abstraction with graceful fallback
  - Secondary / Docling: `docling` abstraction with graceful fallback
  - Native Multilingual Engine: High-precision hybrid layout engine utilizing PyMuPDF block extraction, Tesseract OCR for image/mixed regions, heuristic reading order reconstruction, and table detection
- **OCR Engine**: Tesseract OCR via `pytesseract` with multi-language combination support (`eng+tam+hin`) and pre-processing
- **HTML Normalization & Sanitization**: `BeautifulSoup4`, `lxml`, `nh3` (Rust-backed ultra-fast sanitizer)
- **Async Queue / Background Workers**: Durable SQLite-backed job queue with worker concurrency control, cancel, retry, and progress telemetry

### Frontend (React 18 / 19 + TypeScript)
- **Tooling**: Vite, TypeScript (strict mode enabled)
- **State Management & Routing**: React Router v6/v7, Zustand / React Context
- **Editor**: TipTap 2.x (ProseMirror core) with StarterKit, Table, Image, Math, and BlockID extensions
- **UI & Layout**: TailwindCSS, Lucide-react icons
- **Highlighter Engine**: Durable Text Quote & Unicode Code Point Position Anchoring, CSS Custom Highlight API + DOM Range Fallback

### Mobile Integration (React Native / WebView)
- **Bridge Protocol**: Bidirectional typed JSON messaging via `window.ReactNativeWebView.postMessage`
- **Reader Module**: Offline standalone HTML + CSS bundle with responsive layout, dark/light themes, and font scaling

---

## 4. Implementation Phases & Task Checklist

### Phase 1: Environment, Architecture & Workspace Setup
- [x] Inspect host environment (macOS ARM64, Python 3.11, Node v24, Tesseract 162 langs)
- [x] Setup Python 3.11 virtual environment (`.venv`)
- [x] Author `DEVELOPMENT_PLAN.md`, `ARCHITECTURE.md`, `LICENSES.md`
- [ ] Scaffold directory structure per specification: `backend/`, `frontend/`, `reader/`, `shared/`, `storage/`, `samples/`, `scripts/`, `docs/`

### Phase 2: PDF Inspection Engine & Core Database
- [ ] Implement `PDFInspectionService`:
  - Digital vs scanned vs mixed page classification
  - Unicode integrity / corrupt font mapping detection
  - Page dimensions, orientation, and image coverage ratio
  - Structural metadata and inspection diagnostic report
- [ ] Implement SQLite database models (`jobs`, `documents`, `revisions`, `highlights`)
- [ ] Implement durable job queue with state transitions: `QUEUED`, `INSPECTING`, `CONVERTING`, `OCR_PROCESSING`, `NORMALIZING`, `VALIDATING`, `COMPLETED`, `FAILED`, `CANCELED`

### Phase 3: OCR Engine & Multilingual Pipeline
- [ ] Implement `OCRService`:
  - Detection of installed Tesseract language packs
  - Dynamic multi-language parameter formatting (`tam+hin+eng`)
  - Image preprocessing (deskewing, contrast adjustment, thresholding)
  - Page-by-page OCR execution on scanned/image-only regions
  - Provenance tagging (native text vs OCR-generated text)

### Phase 4: Canonical Document Model & Converter Abstraction
- [ ] Implement `CanonicalDocument` schema:
  - Document metadata, revisions, pages, blocks, assets, warnings
  - Block types: `heading`, `paragraph`, `list`, `listItem`, `table`, `image`, `caption`, `blockquote`, `equation`, `code`, `pageBreak`
  - Stable, deterministic block IDs (`blk-<page>-<seq>-<hash>`)
  - Reading order preservation and inline formatting spans
- [ ] Implement Converter interface (`PDFConverter` base class)
- [ ] Implement `MarkerConverter` (with availability detection & fallback)
- [ ] Implement `DoclingConverter` (with availability detection & fallback)
- [ ] Implement `NativeHybridConverter` (guaranteed, local zero-cloud fallback preserving full structure)
- [ ] Implement `ConversionOrchestrator` supporting `AUTO`, `MARKER`, `DOCLING`, `NATIVE`

### Phase 5: Semantic HTML Generation, Normalization & Quality Validation
- [ ] Implement `HTMLGenerationService`:
  - Strict semantic tag emission (`<article>`, `<section>`, `<h1-6>`, `<p>`, `<table>`, `<figure>`)
  - Language (`lang`) and directionality (`dir="rtl"|"ltr"`) attributes
  - Responsive, offline-safe CSS generation
  - MathML / LaTeX equation preservation
- [ ] Implement `HTMLNormalizationService`:
  - Tag normalization, whitespace safety (preserving Indic combining marks)
  - Image asset path resolution to relative offline links
  - `nh3` security sanitization (stripping dangerous scripts/events while preserving `data-block-id`)
- [ ] Implement `DocumentQualityService`:
  - Structural integrity scoring, text coverage, missing asset checks, broken link checks
  - Categorization into `PASS`, `WARNING`, `REQUIRES_REVIEW`, `FAILED`

### Phase 6: Durable Persistent Highlighting Engine
- [ ] Implement Unicode code point vs UTF-16 conversion helpers
- [ ] Implement Text Quote (`exact`, `prefix`, `suffix`) & Text Position Anchoring (`start`, `end`)
- [ ] Implement CSS Custom Highlight API with DOM Range fallback
- [ ] Support multi-paragraph, multi-inline, cross-node highlights
- [ ] Implement re-anchoring algorithm on document revision/change
- [ ] Implement CRUD REST APIs for highlights

### Phase 7: React Frontend & TipTap Editor
- [ ] Scaffold Vite + React + TypeScript frontend
- [ ] Build Dashboard Screen (stats, active jobs, completed documents)
- [ ] Build Batch PDF Upload Screen (drag-and-drop, validation, options)
- [ ] Build Conversion Queue Screen (status, progress bar, cancel/retry actions)
- [ ] Build Document Preview Screen (side-by-side original PDF vs converted HTML)
- [ ] Build TipTap HTML Editor (editing blocks, tables, images, revision saving)
- [ ] Build Reader Preview Screen (search, font resizing, theme toggling, highlight controls)
- [ ] Build Export Screen (ZIP bundle, standalone HTML, JSON AST, Quality Report)

### Phase 8: Mobile Integration & React Native WebView Bridge
- [ ] Implement standalone `reader.html` and `reader.js`
- [ ] Implement bidirectional bridge using `window.ReactNativeWebView.postMessage`
- [ ] Typed message protocols: `READER_READY`, `TEXT_SELECTED`, `HIGHLIGHT_CREATED`, `FONT_SIZE_CHANGED`, etc.
- [ ] React Native runnable example app and integration guide

### Phase 9: Testing, Benchmarking & Documentation
- [ ] Unit tests for PDF inspection, OCR, Canonical Model, HTML generation, and highlighting
- [ ] Integration tests on sample PDFs (English, Tamil, Hindi, Arabic RTL, Chinese, complex tables, equations, scanned)
- [ ] Security test cases (XSS, path traversal, corrupt PDFs)
- [ ] Author all 14 comprehensive markdown documentation guides
- [ ] Final verification of all user workflows

---

## 5. Acceptance Criteria
1. Backend launches locally without cloud dependencies.
2. Frontend launches locally and allows batch uploading multiple PDFs.
3. Every PDF is converted into clean, semantic HTML with actual selectable text nodes.
4. Text selection, copying, and persistent highlighting function flawlessly across reloads.
5. Multilingual Indic (Tamil, Hindi) and RTL (Arabic) scripts preserve shaping, combining characters, and text direction.
6. TipTap editor loads and edits the canonical HTML without losing structural integrity.
7. Standalone ZIP exports render completely offline with all images, stylesheets, and fonts.
8. Automated test suite passes covering unit, integration, and security test cases.


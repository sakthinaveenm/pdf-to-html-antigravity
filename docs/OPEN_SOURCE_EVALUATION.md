# Comprehensive Open-Source Evaluation Report

This report documents the rigorous evaluation of existing open-source projects, libraries, frameworks, and pretrained models considered for the **Multilingual PDF to HTML Conversion Platform**. In adherence to the **Open-Source-First Development Requirement**, every architectural component was evaluated against 12 critical criteria before adoption or customization.

---

## Evaluation Criteria Matrix

1. **Functionality & Accuracy**: Fidelity of extraction, reading order, table parsing, and equation preservation.
2. **Multilingual Support**: Coverage across Indic (Tamil, Hindi, etc.), Semitic RTL (Arabic, Urdu), and CJK scripts.
3. **Unicode & Indic Script Compatibility**: Integrity of combining vowel marks, viramas, and complex script shaping.
4. **Selectable HTML Text Output**: Real DOM text nodes without canvas, SVG glyph hacks, or character spans.
5. **React Native WebView Compatibility**: Clean reflow and script execution on Android WebView and iOS WKWebView.
6. **Offline / Local Execution**: Operates 100% locally with zero external network or hosted API requirements.
7. **CPU & Low-VRAM Compatibility**: Runs within a 16 GB RAM and 4 GB VRAM budget (or CPU fallback).
8. **Maintenance Activity**: Commit frequency, release cadence, active issue resolution, and community size.
9. **License Compatibility**: Source code and model-weight licensing for permissive and commercial deployment.
10. **Security Vulnerabilities**: Attack surface, sandbox escapes, memory safety, and XSS sanitization.
11. **Integration Complexity**: Python/TypeScript SDK ergonomics, clean packaging, and dependency surface.
12. **Long-Term Maintainability**: Extensibility, stable public APIs, and lock-in avoidance.

---

## Detailed Project Evaluations

### 1. Marker
- **Repository**: [https://github.com/datalab-to/marker](https://github.com/datalab-to/marker)
- **Purpose**: High-accuracy PDF-to-Markdown/HTML conversion using Surya layout and OCR models.
- **Source License**: GPL v3
- **Model Weight License**: CC-BY-NC-4.0 (Commercial restrictions on raw Surya weights)
- **Latest Tested Version**: 2.1.0
- **Maintenance Status**: Very Active (weekly commits, fast-growing community).
- **Supported Output Formats**: Markdown, HTML, JSON element tree.
- **Multilingual Capabilities**: Strong Latin/European and CJK coverage; moderate Indic coverage via Surya OCR.
- **Hardware Requirements**: Minimum 4 GB VRAM for GPU mode; supports CPU inference with increased latency.
- **Advantages**:
  - Exceptional extraction of complex academic layouts, multi-column articles, and LaTeX equations.
  - Built-in heuristic reading order reassembly.
  - Provides memory cleanup hooks (`shutdown_models()`).
- **Limitations**:
  - CC-BY-NC-4.0 model weight license restricts unencumbered commercial distribution without custom licensing.
  - Heavy memory footprint (~2-3 GB RAM when PyTorch models are resident).
- **Integration Decision**: **Integrated as Optional Neural Converter** (`MarkerConverter`).
- **Reason**: Excellent for academic paper layout parsing, but shielded behind our `PDFConverter` abstract interface and lazy loading so users can choose Docling or Native if GPL/CC-BY-NC licenses do not fit their deployment model.

---

### 2. IBM Docling
- **Repository**: [https://github.com/docling-project/docling](https://github.com/docling-project/docling)
- **Purpose**: Deep document understanding, reading order preservation, and rich tabular extraction.
- **Source License**: MIT License
- **Model Weight License**: Apache 2.0 / MIT (IBM Docling models)
- **Latest Tested Version**: 2.147.0
- **Maintenance Status**: Extremely Active (backed by IBM Research, multi-release monthly cadence).
- **Supported Output Formats**: HTML5, Markdown, DoclingDocument JSON AST, DocTags.
- **Multilingual Capabilities**: Broad multilingual coverage with RapidOCR and pluggable OCR engines.
- **Hardware Requirements**: Runs on CPU (Apple Silicon MPS / Intel / AMD) and CUDA GPU.
- **Advantages**:
  - Fully permissive MIT license for both source code and model weights (commercial-safe).
  - Best-in-class table extraction, preserving header hierarchies, rowspans, and colspans.
  - Native export to clean semantic HTML and structured JSON AST.
- **Limitations**:
  - Substantial wheel size and dependencies (torch, torchvision, transformers).
- **Integration Decision**: **Integrated as Primary Neural Converter** (`DoclingConverter`).
- **Reason**: Fully permissive licensing, superior table extraction, robust CPU execution, and native HTML generation align directly with commercial-ready local deployment.

---

### 3. MinerU (Magic-PDF)
- **Repository**: [https://github.com/opendatalab/MinerU](https://github.com/opendatalab/MinerU)
- **Purpose**: Deep-learning extraction for complex layout analysis, mathematical formulas, and scanned books.
- **Source License**: Apache 2.0
- **Model Weight License**: OpenDataLab Academic / Open Weights (various sub-models).
- **Latest Tested Version**: v0.9+
- **Maintenance Status**: Active.
- **Supported Output Formats**: Markdown, JSON.
- **Multilingual Capabilities**: High precision on Chinese and English; limited native training on South Asian Indic scripts (Tamil, Telugu, Kannada, Malayalam).
- **Hardware Requirements**: High GPU requirements (typically recommends 8 GB+ VRAM; struggles under 4 GB VRAM limit).
- **Advantages**: High fidelity on East Asian CJK academic textbooks and dense mathematical proofs.
- **Limitations**: High VRAM consumption (>6 GB for full YOLO/layout pipeline), high integration complexity, and lack of specialized Tamil/Indic script optimizations.
- **Integration Decision**: **Evaluated and Deferred**.
- **Reason**: Exceeds the target 4 GB VRAM / CPU constraint and provides inferior Indic script accuracy compared to Tesseract 5.x + PyMuPDF. Docling and Marker cover the neural use case more safely within the memory budget.

---

### 4. pdf2htmlEX
- **Repository**: [https://github.com/pdf2htmlex/pdf2htmlex](https://github.com/pdf2htmlex/pdf2htmlex)
- **Purpose**: Exact visual reproduction of PDF pages in fixed-layout HTML/CSS.
- **Source License**: GPL v3
- **Latest Tested Version**: 0.18.8
- **Maintenance Status**: Semi-maintained (community forks).
- **Supported Output Formats**: Single-page fixed HTML with absolute CSS positioning.
- **Multilingual Capabilities**: Renders any glyph through embedded web fonts.
- **Hardware Requirements**: Very light CPU usage.
- **Advantages**: Exact pixel-perfect visual fidelity matching the source PDF.
- **Limitations**:
  - Uses absolute positioning (`position: absolute; left: 142px; top: 310px;`) for every text span.
  - Destroys responsive reflow: unreadable on mobile screens and React Native WebViews.
  - Breaks standard rich-text editing in TipTap/ProseMirror (blocks cannot be edited naturally).
  - Frequently wraps individual words or letters in disconnected spans.
- **Integration Decision**: **Rejected as Primary Document Representation**.
- **Reason**: The project requirements explicitly prioritize semantic HTML, responsive text flow, and editor compatibility over pixel-perfect fixed positioning.

---

### 5. Mozilla PDF.js
- **Repository**: [https://github.com/mozilla/pdf.js](https://github.com/mozilla/pdf.js)
- **Purpose**: Client-side PDF rendering in standard web technologies.
- **Source License**: Apache 2.0
- **Latest Tested Version**: v4.x
- **Maintenance Status**: Highly Active (maintained by Mozilla).
- **Supported Output Formats**: Canvas render with overlay text layer.
- **Multilingual Capabilities**: Full PDF spec font rendering.
- **Hardware Requirements**: Client-side browser execution.
- **Advantages**:
  - Industry-standard viewer for original PDF verification.
  - Zero server-side GPU or CPU load.
- **Limitations**:
  - Text layer is designed only for selection matching over canvas, not for editable or responsive document semantics.
- **Integration Decision**: **Integrated for Side-by-Side Verification**.
- **Reason**: Used on the left side of `DocumentPreviewScreen` to give users a reliable visual baseline of the original PDF without confusing it with the canonical editable HTML document.

---

### 6. Tesseract OCR & Tessdata
- **Repository**: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) & [tessdata](https://github.com/tesseract-ocr/tessdata)
- **Purpose**: Local optical character recognition for scanned pages and image regions.
- **Source License**: Apache 2.0
- **Tessdata License**: Apache 2.0
- **Latest Tested Version**: 5.5.0
- **Maintenance Status**: Very Active.
- **Supported Output Formats**: Plain text, HOCR, ALTO, PDF, TSV.
- **Multilingual Capabilities**: 162+ language packs, including all 19 target languages (Tamil, Hindi, Telugu, Malayalam, Arabic, Urdu, CJK, etc.). Supports dynamic combination (`eng+tam+hin`).
- **Hardware Requirements**: CPU-optimized (SIMD AVX2 / NEON acceleration); low RAM footprint (<200 MB per page).
- **Advantages**:
  - Zero GPU or VRAM requirements.
  - Unequaled language coverage across Indian languages and complex scripts.
  - Highly robust against missing or corrupt PDF font encodings.
- **Limitations**: Requires clean page binarization and preprocessing for optimal accuracy.
- **Integration Decision**: **Adopted as Core OCR Engine** (`OCRService`).
- **Reason**: Fully open-source, Apache 2.0 licensed, natively fast on CPU, and supports all required multilingual language packs.

---

### 7. TipTap & ProseMirror
- **Repositories**: [https://github.com/ueberdosis/tiptap](https://github.com/ueberdosis/tiptap) and [https://github.com/ProseMirror](https://github.com/ProseMirror)
- **Purpose**: Headless, schema-driven rich text editing framework.
- **Source License**: MIT License
- **Latest Tested Version**: TipTap 2.11.5 / ProseMirror 1.x
- **Maintenance Status**: Extremely Active.
- **Supported Output Formats**: HTML5, ProseMirror JSON AST, Markdown.
- **Multilingual Capabilities**: Full native browser IME support (Tamil, Devanagari, Arabic RTL, CJK).
- **Hardware Requirements**: Client-side browser.
- **Advantages**:
  - Strong schema constraints preventing invalid HTML generation.
  - Native table support with resizable columns and headers (`@tiptap/extension-table`).
  - Extensible attribute preservation (`data-block-id`).
  - Seamless bidirectional mapping between our `CanonicalDocument` AST and ProseMirror nodes.
- **Limitations**: Requires custom extensions to ensure custom `data-block-id` attributes are retained across block splits.
- **Integration Decision**: **Adopted as HTML Editor Engine** (`EditorScreen.tsx`).
- **Reason**: Established, robust, MIT licensed, and eliminates the need to reinvent a complex contenteditable engine.

---

### 8. Hypothesis Client & W3C Web Annotation Architecture
- **Repository**: [https://github.com/hypothesis/client](https://github.com/hypothesis/client)
- **Purpose**: Standards-compliant web text annotation and highlighting.
- **Source License**: BSD-2-Clause
- **Maintenance Status**: Active.
- **Architectural Contribution**:
  - Pioneered the W3C Web Annotation Data Model using dual anchoring: **TextQuoteSelector** (`exact`, `prefix`, `suffix`) and **TextPositionSelector** (`start`, `end`).
  - Solved highlight resilience across DOM changes, re-renders, and font size changes.
- **Integration Assessment**:
  - Embedding the entire Hypothesis client pulls in heavy dependencies, authentication layers, and external service assumptions.
  - Reusing their core selector architecture within a lightweight, zero-dependency adapter tailored for React Native WebViews provides a faster, cleaner solution.
- **Integration Decision**: **Architectural Reuse via Lightweight Adapter** (`reader/src/selection_highlighter.js` and `backend/app/services/annotations/highlight_service.py`).
- **Reason**: Fully adheres to W3C Web Annotation standards, handles Unicode codepoints vs UTF-16 code units, and leverages the modern CSS Custom Highlight API without the weight of the full Hypothesis server.

---

### 9. HTML Processing: BeautifulSoup4, lxml, and nh3
- **Repositories**:
  - BeautifulSoup4 (MIT)
  - lxml (BSD-3-Clause)
  - nh3 (MIT / Apache 2.0)
- **Purpose**:
  - `BeautifulSoup4` + `lxml`: DOM tree inspection, tag normalization, and element hierarchy validation.
  - `nh3`: Rust-backed HTML sanitization protecting against XSS and unsafe script execution.
- **Integration Decision**: **Adopted as Standard HTML Processing Suite**.
- **Reason**: High performance, memory safety, and complete control over preserved custom attributes (`data-block-id`, `data-page`, `dir`, `lang`).

---

## Summary Selection Matrix

| Subsystem | Selected Project / Library | Primary Alternative Evaluated | Key Rationale for Selection |
|---|---|---|---|
| Primary Neural Converter | **Docling** | Marker | MIT license for code & model weights; superior table extraction; reliable CPU execution. |
| Optional Neural Converter | **Marker** | MinerU | Best-in-class multi-column academic paper layout; lazy model loading with memory shutdown. |
| High-Speed Zero-Cloud Converter | **Native Hybrid (PyMuPDF + Tesseract)** | pdf2htmlEX | Semantic responsive HTML text nodes instead of fixed absolute positioning; ultra-fast. |
| OCR Engine | **Tesseract 5.x** | EasyOCR / PaddleOCR | 162+ language data packs (including 11 Indic scripts); Apache 2.0; CPU-native. |
| HTML Editor | **TipTap (ProseMirror)** | Slate / Quill | Strict schema enforcement; robust table extensions; MIT license. |
| Text Highlighting | **W3C Annotation Adapter (Hypothesis-spec)** | Hypothesis Full Client | Lightweight zero-dependency script optimized for React Native WebView and CSS Highlights. |
| HTML Sanitization | **nh3** | Bleach | Rust-based memory safety; 20x faster than Bleach; explicit tag/attribute whitelisting. |

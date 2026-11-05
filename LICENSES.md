# Open Source Licenses & Model Weights Compliance

## 1. Core Platform License
This platform is licensed under the **Apache License 2.0**.

---

## 2. Backend Libraries License Review

| Component | License | Permissible Usage | Notes |
|-----------|---------|-------------------|-------|
| FastAPI | MIT | Permissive | API framework |
| Pydantic v2 | MIT | Permissive | Data validation |
| SQLAlchemy 2.0 | MIT | Permissive | ORM & database |
| PyMuPDF (`fitz`) | GNU AGPL v3 / Commercial | Copyleft / Commercial | Used for local document geometry parsing |
| pdfplumber | MIT | Permissive | PDF text & table inspection |
| pypdf | BSD-3-Clause | Permissive | PDF metadata inspection |
| pytesseract | Apache 2.0 | Permissive | Tesseract OCR wrapper |
| Pillow (PIL) | HPND | Permissive | Image preprocessing |
| BeautifulSoup4 | MIT | Permissive | HTML parsing |
| lxml | BSD-3-Clause | Permissive | XML/HTML processing |
| nh3 | MIT / Apache 2.0 | Permissive | Rust-based security sanitizer |
| python-bidi | LGPL v3 | Weak Copyleft | RTL text reordering |
| arabic-reshaper | MIT | Permissive | Arabic cursive ligature shaping |
| markdown2 | MIT | Permissive | Markdown parsing |

---

## 3. Converter Engines & Model Weights

### A. Marker (`marker-pdf`)
- **Source Code License**: GPL v3
- **Surya Layout & Recognition Weights**: CC-BY-NC-4.0 / Open weights hosted on HuggingFace Hub.
- **Commercial Note**: If deploying in strict commercial environments with restrictions on CC-BY-NC weights, the platform seamlessly defaults to the `NATIVE` hybrid converter.

### B. IBM Docling (`docling`)
- **Source Code License**: MIT
- **Docling IBM Models**: Apache 2.0 / MIT permissively licensed deep document parsing models.

### C. Tesseract OCR
- **Source Code License**: Apache 2.0
- **Tessdata Language Packs**: Apache 2.0 (Official Google Tesseract traineddata repositories).

---

## 4. Frontend & Editor Licenses

| Component | License | Permissible Usage | Notes |
|-----------|---------|-------------------|-------|
| React & React DOM | MIT | Permissive | UI framework |
| Vite | MIT | Permissive | Build tool |
| TypeScript | Apache 2.0 | Permissive | Type system |
| TipTap 2.x | MIT | Permissive | ProseMirror rich text editor |
| Tailwind CSS | MIT | Permissive | Utility styling |
| Lucide React | ISC | Permissive | Icons |
| react-native-webview | MIT | Permissive | Mobile WebView bridge |

---

## 5. Fonts & Typography
- Standard system fonts (`Noto Sans`, `Devanagari Sangam MN`, `Tamil Sangam MN`, `Arial Unicode MS`, `Geeza Pro`) are utilized without bundling unauthorized proprietary font files.
- Offline reader CSS relies solely on pre-installed system fonts, ensuring zero external font downloading or copyright infringement.


# Third-Party Licenses & Attributions

This document lists all third-party open-source components, libraries, frameworks, models, and datasets integrated into or utilized by the **Multilingual PDF to HTML Conversion Platform**, along with their respective license texts, copyright notices, and compliance obligations.

---

## 1. Backend Python Dependencies

### FastAPI
- **Copyright**: (c) 2018 Sebastián Ramírez
- **License**: MIT License
- **Notice**: Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software...

### Pydantic & Pydantic-Core
- **Copyright**: (c) 2017-present Samuel Colvin and contributors
- **License**: MIT License

### SQLAlchemy
- **Copyright**: (c) 2005-2026 Michael Bayer and contributors
- **License**: MIT License

### IBM Docling & Docling-Core
- **Copyright**: (c) 2024-present IBM Research
- **License**: MIT License
- **Obligations**: Include the original copyright and permission notice in all copies or substantial portions of the Software.

### Marker-PDF
- **Copyright**: (c) 2023-present Vik Paruchuri
- **License**: GNU General Public License v3.0 (GPLv3)
- **Surya Model Weights**: Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC-4.0).
- **Compliance Note**: Marker is integrated through an abstract, modular interface (`PDFConverter`) in `backend/app/services/converters/marker_converter.py`. For commercial environments requiring purely permissive licenses, users can configure the platform to execute IBM Docling (MIT) or the Native Hybrid converter (MIT/Apache 2.0).

### PyMuPDF (fitz)
- **Copyright**: (c) 2016-2026 Artifex Software, Inc.
- **License**: GNU Affero General Public License v3 (AGPLv3) / Commercial License
- **Notice**: Users deploying in proprietary environments requiring non-copyleft licensing may acquire a commercial OEM license from Artifex Software or utilize pdfplumber/pypdf alternatives.

### pdfplumber & pdfminer.six
- **Copyright**: (c) 2015-2026 Jeremy Singer-Vine and contributors
- **License**: MIT License

### pypdf
- **Copyright**: (c) 2006-2008 Mathieu Fenniak, 2022-2026 Martin Thoma and contributors
- **License**: BSD 3-Clause License

### Tesseract OCR & Tessdata
- **Copyright**: (c) 2006-present Google Inc., 1995-1997 Hewlett-Packard Co.
- **License**: Apache License, Version 2.0
- **Obligations**: Users may reproduce and distribute copies of the Work in any medium, with or without modifications, provided that you give any other recipients of the Work or Derivative Works a copy of this License.

### nh3 (Ammonia Python Bindings)
- **Copyright**: (c) 2022-present Messense and contributors
- **License**: MIT License / Apache License 2.0

### BeautifulSoup4
- **Copyright**: (c) 2004-2026 Leonard Richardson
- **License**: MIT License

### lxml
- **Copyright**: (c) 2004-2026 Infrae and contributors
- **License**: BSD 3-Clause License

### python-bidi
- **Copyright**: (c) 2008-2026 Meir Kriheli
- **License**: GNU Lesser General Public License v3.0 (LGPLv3)

### arabic-reshaper
- **Copyright**: (c) 2015-2026 Abdullah Diab
- **License**: MIT License

---

## 2. Frontend Dependencies

### React & React DOM
- **Copyright**: (c) Meta Platforms, Inc. and affiliates
- **License**: MIT License

### TipTap (ProseMirror Core)
- **Copyright**: (c) 2020-present Überdosis GbR
- **License**: MIT License
- **Components**:
  - `@tiptap/react` (MIT)
  - `@tiptap/starter-kit` (MIT)
  - `@tiptap/extension-table` (MIT)
  - `@tiptap/extension-image` (MIT)

### ProseMirror
- **Copyright**: (c) 2015-present Marijn Haverbeke and contributors
- **License**: MIT License

### Vite
- **Copyright**: (c) 2019-present Yuxi (Evan) You and Vite contributors
- **License**: MIT License

### Tailwind CSS
- **Copyright**: (c) Tailwind Labs, Inc.
- **License**: MIT License

### Lucide React
- **Copyright**: (c) 2022-present Lucide Contributors
- **License**: ISC License

---

## 3. Reader & Mobile Bridge

### W3C Web Annotation Architecture (Derived from Hypothesis Principles)
- **Reference**: W3C Recommendation 23 February 2017: Web Annotation Data Model
- **Hypothesis Client Reference**: (c) 2013-2026 Hypothes.is Project and contributors (BSD 2-Clause License).
- **Implementation**: Our standalone `selection_highlighter.js` implements a clean-room, zero-dependency adapter adhering directly to the W3C Web Annotation Selector specification (`TextQuoteSelector` and `TextPositionSelector`).

### React Native WebView Bridge
- **Reference**: `react-native-webview` (MIT License)
- **Copyright**: (c) 2015-present Facebook, Inc., 2018-present React Native Community.

---

## 4. Attributions & Acknowledgments

We gratefully acknowledge the creators, maintainers, and open-source communities behind:
1. **The Tesseract OCR Community** for maintaining comprehensive OCR language data across world languages, particularly for South Asian Indic scripts.
2. **IBM Research and the Docling Project** for advancing open-source document layout parsing and tabular extraction under permissive licenses.
3. **The TipTap and ProseMirror Teams** for creating accessible, schema-driven rich text editing primitives.
4. **The W3C Web Annotation Working Group and Hypothesis Project** for establishing resilient text quote and position anchoring standards.

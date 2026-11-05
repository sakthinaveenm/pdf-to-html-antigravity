# Troubleshooting & Operational Guide

## 1. Tesseract OCR Issues

### Symptom: `TesseractError: (1, 'Error opening data file /.../tam.traineddata')`
**Cause**: The requested language pack (e.g. Tamil `tam`) is not installed in your system's `tessdata` folder.
**Solution**:
- **macOS**: Run `brew install tesseract-lang` (installs all 162+ language data packs).
- **Ubuntu/Debian**: Run `sudo apt-get install tesseract-ocr-tam tesseract-ocr-hin tesseract-ocr-ara`.
- **Windows**: Rerun the Tesseract installer from UB-Mannheim and check "Additional language data".
- Verify: Run `tesseract --list-langs` and ensure the code appears.

---

## 2. Text Encoding & Corrupted Fonts

### Symptom: Extracted text contains `\ufffd` (replacement characters) or nonsensical letters
**Cause**: The PDF font dictionary lacks a valid `/ToUnicode` CMap mapping, or custom font subset glyph IDs are unmapped.
**Solution**:
1. Check document inspection report: It will classify the page as `TEXT_ENCODING_PROBLEM`.
2. Enable **Force OCR** on the upload screen (or pass `force_ocr=True` to the API).
3. The platform will rasterize the page at 300 DPI and apply Tesseract OCR, bypassing the corrupt vector font mapping.

---

## 3. High Memory Utilization or Out-Of-Memory (OOM)

### Symptom: Process terminates unexpectedly during neural conversion on 16 GB RAM / 4 GB VRAM machines
**Cause**: Marker or Docling layout models require substantial memory when converting large PDFs concurrently.
**Solution**:
1. Ensure `MAX_CONCURRENT_WORKERS=1` in `.env` (default).
2. Set `DEFAULT_CONVERTER=NATIVE`. The Native Hybrid engine converts pages at ultra-high speed (<100 MB RAM usage) without downloading or running multi-gigabyte neural models.
3. If using Marker or Docling, limit batches to fewer than 50 pages per job.

---

## 4. Arabic or Hebrew Text Appears Backwards

### Symptom: Arabic characters are reversed or disconnected (e.g. `ةيبرعلا`)
**Cause**: PDF streams contain raw glyphs in visual LTR layout order.
**Solution**:
- The platform automatically passes detected Arabic/Urdu text through `python-bidi` and `arabic-reshaper`.
- Ensure generated HTML includes `dir="rtl"`.
- If custom CSS is applied, ensure `direction: rtl` and appropriate Arabic font families are loaded (`Geeza Pro`, `Arial`, `Noto Sans Arabic`).

---

## 5. React Native WebView Highlight Issues

### Symptom: Highlights fail to render on older Android devices
**Cause**: Android System WebView version < 105 does not support the modern `CSS.highlights` API.
**Solution**:
- The provided `reader/src/selection_highlighter.js` automatically detects `window.CSS && CSS.highlights`.
- On older devices, it seamlessly falls back to DOM `<mark class="doc-highlight">` wrapping.
- Ensure your React Native WebView component has `javaScriptEnabled={true}` and `originWhitelist={['*']}`.

---

## 6. SQLite Database Concurrency / WAL Mode

### Symptom: `database is locked` error during high-frequency API polling
**Cause**: SQLite default journal mode can lock on simultaneous reads/writes.
**Solution**:
- The platform automatically executes `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` on database connection.
- SQLite WAL (Write-Ahead Logging) allows concurrent readers alongside a single active writer without lock contention.

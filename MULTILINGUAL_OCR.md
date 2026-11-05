# Multilingual OCR & Script Processing Guide

## 1. Supported Multilingual Scripts & Target Languages

The platform provides first-class support for 19 target languages across 4 major script families:

| Language | ISO / BCP-47 | Script Family | Direction | Tesseract Code | Special Processing |
|----------|--------------|---------------|-----------|----------------|---------------------|
| English | `en` / `en-US` | Latin | LTR | `eng` | Baseline |
| Tamil | `ta` / `ta-IN` | Indic (Dravidian) | LTR | `tam` | Preserves virama & kombu vowel signs |
| Hindi | `hi` / `hi-IN` | Indic (Devanagari) | LTR | `hin` | Preserves conjuncts & matras |
| Telugu | `te` / `te-IN` | Indic (Dravidian) | LTR | `tel` | Preserves vowel ligatures |
| Malayalam | `ml` / `ml-IN` | Indic (Dravidian) | LTR | `mal` | Preserves chillu characters |
| Kannada | `kn` / `kn-IN` | Indic (Dravidian) | LTR | `kan` | Preserves ottakshara signs |
| Bengali | `bn` / `bn-BD` | Indic (Bengali) | LTR | `ben` | Preserves hasant & nukta |
| Marathi | `mr` / `mr-IN` | Indic (Devanagari) | LTR | `mar` | Preserves ra-kars |
| Gujarati | `gu` / `gu-IN` | Indic (Gujarati) | LTR | `guj` | Preserves vowel signs without shirorekha |
| Punjabi | `pa` / `pa-IN` | Indic (Gurmukhi) | LTR | `pan` | Preserves addak and tippi |
| Sanskrit | `sa` / `sa-IN` | Indic (Devanagari) | LTR | `san` | Vedic accents & visarga |
| Arabic | `ar` / `ar-SA` | Semitic | RTL | `ara` | Logical bidi reordering, `dir="rtl"` |
| Urdu | `ur` / `ur-PK` | Semitic (Nastaliq) | RTL | `urd` | Nastaliq baseline shaping, `dir="rtl"` |
| Chinese (Simp) | `zh` / `zh-CN` | CJK Ideographic | LTR | `chi_sim` | CJK word-break: break-all |
| Japanese | `ja` / `ja-JP` | CJK (Kana/Kanji) | LTR | `jpn` | Mixed script wrapping |
| Korean | `ko` / `ko-KR` | CJK (Hangul) | LTR | `kor` | Hangul syllable blocks |
| French | `fr` / `fr-FR` | Latin | LTR | `fra` | Accented characters (é, è, ç) |
| German | `de` / `de-DE` | Latin | LTR | `deu` | Umlauts (ä, ö, ü) and eszett (ß) |
| Spanish | `es` / `es-ES` | Latin | LTR | `spa` | Inverted punctuation (¿, ¡), ñ |

---

## 2. Dynamic Language Pack Validation

When an OCR request arrives, `OCRService.validate_languages(requested_langs)` verifies the requested language codes against the local Tesseract installation:
- If a pack is present (e.g. `tam`, `hin`), it is included in the execution argument `--oem 1 -l eng+tam+hin`.
- If a pack is missing, the service:
  1. Continues processing with the remaining available languages.
  2. Emits an actionable diagnostic warning instructing the administrator how to install the missing language data (e.g. `brew install tesseract-lang` or `apt-get install tesseract-ocr-tam`).
  3. Never fabricates a 100% success claim when a language pack was omitted.

---

## 3. Image Preprocessing Pipeline

Scanned pages or image crops undergo image preprocessing before Tesseract inference:
1. **Grayscale Conversion**: Eliminates color noise and tinted background artifacts.
2. **Auto-Contrast (Cutoff 2%)**: Stretches the dynamic range, brightening yellowed paper and deepening faded ink.
3. **Unsharp Masking (`radius=1.5`, `percent=150`, `threshold=3`)**: Clarifies delicate Indic script loops (such as Tamil `ர`, `க` or Devanagari `र`, `क`).

---

## 4. Indic Script & Unicode Integrity Rules

1. **No Combining Mark Stripping**: Unicode combining marks (`U+0901`–`U+097F`, `U+0B80`–`U+0BFF`) must never be stripped during normalization.
2. **True DOM Text Nodes**: Characters are never rendered as SVG glyphs or canvas pixels.
3. **No Character-Level Span Splitting**: Avoids wrapping each letter in its own `<span>`, which breaks native complex script shaping engines (HarfBuzz, DirectWrite, CoreText).

---

## 5. Bidirectional (RTL) Text Reordering

In vector PDF streams, Arabic words are frequently stored in physical visual order from left-to-right (e.g., `اهبادآو ةيبرعلا ةغللا خيرات`).
When rendered directly into HTML without transformation, browser layout engines reverse the already-reversed visual text, producing corrupt reading orders.
The platform integrates `python-bidi` and `arabic-reshaper`:
- Detects Arabic and Urdu script codepoint ranges (`0x0600`–`0x06FF`).
- Applies `get_display()` to invert physical visual order into **logical Unicode reading order** (`تاريخ اللغة العربية وآدابها`).
- Emits `<p dir="rtl" lang="ar">` attributes so the browser renders right-aligned, connected cursive text nodes.

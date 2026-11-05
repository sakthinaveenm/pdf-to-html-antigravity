# Durable Text Selection & Persistent Highlighting Engine

## 1. System Overview

Persistent text selection and highlighting is a core capability of this platform. It allows users in Web browsers, HTML editors, and React Native WebViews (iOS and Android) to:
- Select a word, part of a sentence, or entire sentences
- Select across inline formatted tags (`<strong>`, `<em>`, `<a>`, `<span>`)
- Select across multiple paragraphs
- Persist annotations to local SQLite storage
- Restore annotations across page reloads, font size changes, and document revisions
- Remove and update annotation colors

---

## 2. Dual-Anchoring Model

Annotations use **dual anchoring** conforming to the W3C Web Annotation Data Model:

```json
{
  "id": "hl-9f20a1bc",
  "documentId": "4c9470d0-fb16-46b0-96f7-4638a143f550",
  "revision": 1,
  "blockIds": ["blk-p1-s002-c9d2"],
  "quote": {
    "exact": "தமிழ் ஒரு அழகான மொழி",
    "prefix": "அறிமுகம்: ",
    "suffix": ". இது செம்மொழியாகும்."
  },
  "position": {
    "start": 10,
    "end": 31,
    "unit": "unicode-codepoint"
  },
  "color": "#FFEB3B",
  "note": "Important linguistic note",
  "resolved": true
}
```

### Text Quote Anchoring
- `exact`: The exact string of selected characters.
- `prefix`: 32 characters immediately preceding the selection in the block.
- `suffix`: 32 characters immediately following the selection in the block.
- Purpose: Guarantees that even if text shifts due to edits elsewhere in the block or document, the annotation can be relocated deterministically.

### Text Position Anchoring (Unicode Codepoints)
- `start`: 0-based character index from block start.
- `end`: 0-based character index from block start.
- `unit`: `"unicode-codepoint"` (NOT UTF-16 code units).

---

## 3. Unicode Codepoints vs. JavaScript UTF-16 Offsets

JavaScript strings and DOM `Range.startOffset` count **UTF-16 code units**, not Unicode codepoints:
- Characters in the Basic Multilingual Plane (BMP) occupy 1 UTF-16 code unit (e.g., Latin `A`, Tamil `த`, Arabic `ع`).
- Characters in Supplementary Planes (SMP) occupy 2 UTF-16 code units (surrogate pairs, such as emojis 🚀 or rare CJK ideographs).
- Indic scripts use combining vowel signs (matras, viramas). For example, `கி` consists of `க` (U+0B95) + `ி` (U+0BC7) = 2 codepoints.

### Helper Conversions
- `utf16_offset_to_codepoint_offset(text, utf16_offset)`: Iterates string characters, converting UTF-16 code unit offsets to true Unicode codepoints for durable storage.
- `codepoint_offset_to_utf16_offset(text, codepoint_offset)`: Reconstructs exact DOM Range boundaries during restoration in JavaScript.

---

## 4. Dual Rendering Architecture

### Primary: CSS Custom Highlight API
- Supported in modern browsers (Chrome 105+, Safari 17.2+, Edge 105+).
- **Zero DOM Tree Mutation**: Creates a `new Highlight(range)` and sets it into `CSS.highlights.set(id, highlight)`.
- **Performance**: 60fps scrolling and zero interference with ProseMirror/TipTap editor DOM trees.

### Fallback: DOM `<mark>` Wrapping
- For older WebViews (e.g. legacy Android system WebViews), the engine safely extracts the Range contents and wraps them in:
```html
<mark class="doc-highlight" data-highlight-id="hl-9f20a1bc" style="background-color: #FFEB3B;">
  தமிழ் ஒரு அழகான மொழி
</mark>
```

---

## 5. Re-anchoring Algorithm on Document Revision

When a user edits document HTML and saves a new revision:
1. `AnnotationService.reanchor_highlights_on_revision()` is invoked with the updated text of each block.
2. For each highlight:
   - Evaluates if `exact` exists in the updated block text.
   - If multiple occurrences exist, disambiguates using `prefix + exact + suffix`.
   - If matched, recalculates `start_offset` and `end_offset`, updates `revision = new_revision`, and marks `resolved = true`.
   - If the text was deleted, marks `resolved = false` instead of placing the annotation on incorrect content.

# Semantic HTML Output Specification

## 1. Output Document Structure

All generated documents adhere to strict HTML5 standards using real DOM text nodes:

```html
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>தமிழ் இலக்கிய வரலாறு</title>
  <style>
    /* Inlined Responsive Offline Reader CSS */
  </style>
</head>
<body>
  <div class="document-container">
    <article class="canonical-document" lang="ta" data-document-id="doc-7a2e81">
      <section data-page="1">
        <h1 id="blk-p1-s001-a4b1" data-block-id="blk-p1-s001-a4b1">
          தமிழ் இலக்கியம்
        </h1>

        <p id="blk-p1-s002-c9d2" data-block-id="blk-p1-s002-c9d2" dir="ltr" lang="ta">
          தமிழ் ஒரு மிகத் தொன்மையான செம்மொழியாகும்.
        </p>

        <figure id="blk-p1-s003-f3e7" data-block-id="blk-p1-s003-f3e7">
          <img src="./assets/img_p1_0_xref12.png" alt="Figure on page 1" loading="lazy" />
          <figcaption>படம் 1: பண்டைய தமிழ் ஓலைச்சுவடிகள்</figcaption>
        </figure>

        <div class="table-responsive">
          <table id="blk-p1-s004-b8e1" data-block-id="blk-p1-s004-b8e1">
            <thead>
              <tr>
                <th>நூல்</th>
                <th>ஆசிரியர்</th>
                <th>காலம்</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>திருக்குறள்</td>
                <td>திருவள்ளுவர்</td>
                <td>கி.மு. 1-ஆம் நூற்றாண்டு</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section data-page="2">
        <h2 id="blk-p2-s005-d1f4" data-block-id="blk-p2-s005-d1f4">
          காப்பியங்கள்
        </h2>
        <p id="blk-p2-s006-e2a9" data-block-id="blk-p2-s006-e2a9" dir="ltr" lang="ta">
          சிலப்பதிகாரம் மற்றும் மணிமேகலை இரட்டைக் காப்பியங்கள் என அழைக்கப்படுகின்றன.
        </p>
      </section>
    </article>
  </div>
</body>
</html>
```

---

## 2. Key Design Constraints

1. **No Canvas Rendering**: Readable text is never placed inside `<canvas>` elements.
2. **No SVG Outlines as Text**: Text nodes are standard UTF-8 string nodes.
3. **No Character-Spans**: Text flows in natural paragraph and heading blocks.
4. **No Absolute Positioning Hacks**: Responsive flow allows dynamic reflow when users increase font size or switch between mobile and desktop viewports.
5. **Deterministic Block IDs**: Every block has `data-block-id="blk-p{page}-s{seq}-{hash}"`, enabling persistent highlight anchoring across revisions.

---

## 3. Responsive Offline Reader CSS

### Design Variables
- `--bg-primary`: `#ffffff` (light), `#121212` (dark), `#f8f1e3` (sepia)
- `--text-primary`: `#1a1a1a` (light), `#e0e0e0` (dark), `#433422` (sepia)
- `--font-indic`: `"Tamil Sangam MN"`, `"Devanagari Sangam MN"`, `"Noto Sans"`, sans-serif
- `--highlight-yellow`: `#fff3a8`

### Typography & Reflow
- CJK Line Breaking: `[lang="zh"], [lang="ja"], [lang="ko"] { word-break: break-all; }`
- RTL Support: `[dir="rtl"] { direction: rtl; text-align: right; }`
- Tables: Wrapped in `.table-responsive` with `-webkit-overflow-scrolling: touch` for mobile WebViews.

---

## 4. Security & Sanitization (`nh3`)

Uploaded PDFs are treated as untrusted files. All generated or edited HTML passes through `HTMLNormalizationService`:
- Strips `<script>`, `<iframe>`, `<object>`, `<embed>`, `<form>`, `<input>`.
- Strips event attributes (`onclick`, `onerror`, `onload`).
- Strips dangerous URL schemes (`javascript:`, `vbscript:`).
- Preserves all safe document formatting and semantic attributes (`data-block-id`, `data-page`, `data-highlight-id`, `dir`, `lang`, `src`, `alt`).

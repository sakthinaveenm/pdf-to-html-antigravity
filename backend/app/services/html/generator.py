"""
Semantic HTML Generation Service.
Generates clean, accessible, semantic HTML5 with stable block IDs,
language/direction attributes, MathML/LaTeX preservation, responsive typography,
and offline reader stylesheets.
"""
from typing import List, Dict, Any, Optional
import html
from backend.app.schemas.canonical import CanonicalDocument, DocumentBlock

READER_CSS = """
/* Responsive Offline Reader Stylesheet */
:root {
  --bg-primary: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #555555;
  --border-color: #e5e7eb;
  --highlight-yellow: #fff3a8;
  --font-base: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-indic: "Tamil Sangam MN", "Devanagari Sangam MN", "Noto Sans", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

[data-theme="dark"] {
  --bg-primary: #121212;
  --text-primary: #e0e0e0;
  --text-secondary: #aaaaaa;
  --border-color: #333333;
  --highlight-yellow: #5c4d00;
}

[data-theme="sepia"] {
  --bg-primary: #f8f1e3;
  --text-primary: #433422;
  --text-secondary: #705d45;
  --border-color: #e2d7c5;
  --highlight-yellow: #fae08c;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-base), var(--font-indic);
  font-size: 16px;
  line-height: 1.65;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.document-container {
  max-width: 860px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}

article {
  display: block;
}

section[data-page] {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px dashed var(--border-color);
  position: relative;
}

section[data-page]::after {
  content: "Page " attr(data-page);
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: right;
  margin-top: 1.5rem;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.3;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

h1 { font-size: 2.1rem; }
h2 { font-size: 1.7rem; }
h3 { font-size: 1.35rem; }
h4 { font-size: 1.15rem; }

p {
  margin: 0 0 1.25em 0;
  text-align: justify;
}

/* RTL Language Handling */
[dir="rtl"] {
  direction: rtl;
  text-align: right;
}

/* Indic Script Shaping */
[lang="ta"], [lang="hi"], [lang="te"], [lang="ml"], [lang="kn"], [lang="bn"], [lang="mr"], [lang="gu"] {
  font-family: var(--font-indic), var(--font-base);
  letter-spacing: 0.01em;
}

/* CJK line wrapping */
[lang="zh"], [lang="ja"], [lang="ko"] {
  word-break: break-all;
}

/* Tables */
.table-responsive {
  overflow-x: auto;
  margin: 1.5rem 0;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
  font-size: 0.95rem;
}

th, td {
  border: 1px solid var(--border-color);
  padding: 0.65rem 0.85rem;
  text-align: left;
}

th {
  background-color: rgba(128, 128, 128, 0.08);
  font-weight: 600;
}

/* Images & Figures */
figure {
  margin: 2rem 0;
  text-align: center;
}

figure img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

figcaption {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

/* Equations */
.math-equation {
  display: block;
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: rgba(128, 128, 128, 0.05);
  border-radius: 6px;
  text-align: center;
  font-family: var(--font-mono);
  overflow-x: auto;
}

/* Code Blocks */
pre {
  background-color: rgba(128, 128, 128, 0.08);
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 0.9rem;
}

blockquote {
  border-left: 4px solid #3b82f6;
  margin: 1.5em 0;
  padding: 0.5em 1em;
  color: var(--text-secondary);
  font-style: italic;
}

/* Highlights */
::highlight(doc-highlight) {
  background-color: var(--highlight-yellow);
  color: inherit;
}

mark.doc-highlight {
  background-color: var(--highlight-yellow);
  color: inherit;
  padding: 2px 0;
  border-radius: 2px;
}

/* Responsive adjustment for Mobile */
@media (max-width: 640px) {
  .document-container {
    padding: 1.25rem 1rem;
  }
  h1 { font-size: 1.65rem; }
  h2 { font-size: 1.35rem; }
  p { text-align: left; }
}
"""

class HTMLGenerationService:
    def get_reader_css(self) -> str:
        return READER_CSS

    def generate_html(self, doc: CanonicalDocument, standalone: bool = True) -> str:
        """
        Generate semantic HTML from the CanonicalDocument.
        standalone=True wraps inside <html><head><style>...</style></head><body>...</body></html>.
        """
        # Group blocks by source page
        pages_dict: Dict[int, List[DocumentBlock]] = {}
        for block in doc.blocks:
            page = block.sourcePage or 1
            if page not in pages_dict:
                pages_dict[page] = []
            pages_dict[page].append(block)

        body_parts: List[str] = []
        body_parts.append(f'<article class="canonical-document" lang="{html.escape(doc.language)}" data-document-id="{html.escape(doc.documentId)}">')

        sorted_pages = sorted(pages_dict.keys())
        if not sorted_pages:
            sorted_pages = [1]

        for p_num in sorted_pages:
            blocks = pages_dict.get(p_num, [])
            body_parts.append(f'  <section data-page="{p_num}">')

            for block in blocks:
                b_id = html.escape(block.blockId)
                b_dir = f' dir="{block.direction}"' if block.direction in ("rtl", "ltr") else ''
                b_lang = f' lang="{html.escape(block.language)}"' if block.language else ''
                content_escaped = html.escape(block.content)

                if block.blockType == "heading":
                    lvl = block.level or 1
                    body_parts.append(f'    <h{lvl} id="{b_id}" data-block-id="{b_id}"{b_dir}{b_lang}>{content_escaped}</h{lvl}>')

                elif block.blockType == "paragraph":
                    body_parts.append(f'    <p id="{b_id}" data-block-id="{b_id}"{b_dir}{b_lang}>{content_escaped}</p>')

                elif block.blockType == "listItem":
                    body_parts.append(f'    <ul><li id="{b_id}" data-block-id="{b_id}"{b_dir}{b_lang}>{content_escaped}</li></ul>')

                elif block.blockType == "table" and block.tableData:
                    body_parts.append(f'    <div class="table-responsive">')
                    body_parts.append(f'      <table id="{b_id}" data-block-id="{b_id}">')
                    if block.tableData.headers:
                        body_parts.append('        <thead><tr>')
                        for h in block.tableData.headers:
                            body_parts.append(f'          <th>{html.escape(h.content)}</th>')
                        body_parts.append('        </tr></thead>')
                    if block.tableData.rows:
                        body_parts.append('        <tbody>')
                        for row in block.tableData.rows:
                            body_parts.append('          <tr>')
                            for cell in row.cells:
                                body_parts.append(f'            <td>{html.escape(cell.content)}</td>')
                            body_parts.append('          </tr>')
                        body_parts.append('        </tbody>')
                    body_parts.append('      </table>')
                    body_parts.append('    </div>')

                elif block.blockType == "image" and block.imageData:
                    img_src = html.escape(block.imageData.src)
                    img_alt = html.escape(block.imageData.alt)
                    caption_html = f'<figcaption>{html.escape(block.imageData.caption)}</figcaption>' if block.imageData.caption else ''
                    body_parts.append(f'    <figure id="{b_id}" data-block-id="{b_id}">')
                    body_parts.append(f'      <img src="{img_src}" alt="{img_alt}" loading="lazy" />')
                    if caption_html:
                        body_parts.append(f'      {caption_html}')
                    body_parts.append('    </figure>')

                elif block.blockType == "equation":
                    formula = html.escape(block.mathFormula or block.content)
                    body_parts.append(f'    <div class="math-equation" id="{b_id}" data-block-id="{b_id}">{formula}</div>')

                elif block.blockType == "code":
                    body_parts.append(f'    <pre id="{b_id}" data-block-id="{b_id}"><code>{content_escaped}</code></pre>')

                elif block.blockType == "blockquote":
                    body_parts.append(f'    <blockquote id="{b_id}" data-block-id="{b_id}"><p>{content_escaped}</p></blockquote>')

                elif block.blockType == "pageBreak":
                    body_parts.append(f'    <hr class="page-break" data-page-break="{p_num}" />')

            body_parts.append('  </section>')

        body_parts.append('</article>')
        inner_html = "\n".join(body_parts)

        if not standalone:
            return inner_html

        title_escaped = html.escape(doc.title or "Document")
        doc_lang = html.escape(doc.language or "en")

        return f"""<!DOCTYPE html>
<html lang="{doc_lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_escaped}</title>
  <style>
{READER_CSS}
  </style>
</head>
<body>
  <div class="document-container">
{inner_html}
  </div>
</body>
</html>"""

html_generation_service = HTMLGenerationService()


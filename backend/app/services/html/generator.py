"""
Semantic HTML Generation Service.
Generates clean, accessible, semantic HTML5 with stable block IDs,
language/direction attributes, MathML/LaTeX preservation, responsive typography,
high-fidelity inline CSS styles for HTML editors, and page-by-page deliverables.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import html
import json
import base64
import shutil

from backend.app.schemas.canonical import CanonicalDocument, DocumentBlock, BlockStyle
from backend.app.constants.languages import is_rtl

READER_CSS = """
/* Responsive Offline Reader Stylesheet */
:root {
  --bg-primary: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #555555;
  --border-color: #e5e7eb;
  --highlight-yellow: #fff3a8;
  --font-base: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-multilingual: "Noto Sans", "Noto Serif", "Noto Sans Arabic", "Noto Sans Hebrew", "Noto Sans Devanagari", "Noto Sans Tamil", "Noto Sans Telugu", "Noto Sans Thai", "Noto Sans CJK SC", "Noto Sans CJK JP", "Noto Sans CJK KR", "Tamil Sangam MN", "Devanagari Sangam MN", sans-serif;
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
  font-family: var(--font-base), var(--font-multilingual);
  font-size: 16px;
  line-height: 1.65;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Right-To-Left (RTL) layout support */
[dir="rtl"] {
  direction: rtl;
  text-align: right;
}

[dir="rtl"] section[data-page]::after {
  text-align: left;
}

[dir="rtl"] ul, [dir="rtl"] ol {
  padding-right: 1.5rem;
  padding-left: 0;
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

p {
  margin-top: 0;
  margin-bottom: 1em;
  text-align: justify;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  margin: 1.5rem 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.95rem;
}

th, td {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
}

th {
  background-color: rgba(0, 0, 0, 0.03);
  font-weight: 600;
}

figure {
  margin: 2rem 0;
  text-align: center;
}

figure img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

figcaption {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
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

    def _build_inline_style(self, style: Optional[BlockStyle], extra_styles: Optional[Dict[str, str]] = None) -> str:
        """Construct inline CSS style attribute string for editor paste fidelity."""
        styles: Dict[str, str] = {}
        if style:
            if style.fontFamily:
                styles["font-family"] = style.fontFamily
            if style.fontSize:
                styles["font-size"] = f"{style.fontSize}px"
            if style.fontWeight:
                styles["font-weight"] = str(style.fontWeight)
            if style.fontStyle and style.fontStyle != "normal":
                styles["font-style"] = style.fontStyle
            if style.color:
                styles["color"] = style.color
            if style.textAlign:
                styles["text-align"] = style.textAlign
            if style.lineHeight:
                styles["line-height"] = str(style.lineHeight)
            if style.marginTop:
                styles["margin-top"] = style.marginTop
            if style.marginBottom:
                styles["margin-bottom"] = style.marginBottom
            if style.textIndent:
                styles["text-indent"] = style.textIndent
            if style.backgroundColor:
                styles["background-color"] = style.backgroundColor

        if extra_styles:
            styles.update(extra_styles)

        if not styles:
            return ""

        css_str = "; ".join(f"{k}: {v}" for k, v in styles.items())
        return f' style="{html.escape(css_str)}"'

    def _resolve_image_src(
        self,
        img_raw: str,
        doc_id: str,
        asset_base_url: Optional[str] = None,
        embed_images_base64: bool = False,
        assets_dir: Optional[Path] = None
    ) -> str:
        """Resolve image source according to developer's asset strategy."""
        asset_file = img_raw.split("/")[-1]

        # 1. Base64 embedding strategy
        if embed_images_base64 and assets_dir:
            file_path = assets_dir / asset_file
            if file_path.exists():
                try:
                    raw_bytes = file_path.read_bytes()
                    ext = file_path.suffix.lstrip(".").lower() or "png"
                    b64_str = base64.b64encode(raw_bytes).decode("ascii")
                    return f"data:image/{ext};base64,{b64_str}"
                except Exception:
                    pass

        # 2. Configurable Asset Base URL strategy (e.g. UEducate CDN)
        if asset_base_url:
            return f"{asset_base_url.rstrip('/')}/{asset_file}"

        # 3. Default API asset route
        if doc_id and (img_raw.startswith("./assets/") or img_raw.startswith("assets/") or not img_raw.startswith("http")):
            return f"/api/v1/documents/{doc_id}/assets/{asset_file}"

        return html.escape(img_raw)

    def generate_block_html(
        self,
        block: DocumentBlock,
        doc_id: str,
        asset_base_url: Optional[str] = None,
        embed_images_base64: bool = False,
        assets_dir: Optional[Path] = None
    ) -> str:
        """Render a single DocumentBlock into semantic HTML with inline CSS."""
        b_id = html.escape(block.blockId)
        b_dir = f' dir="{block.direction}"' if block.direction in ("rtl", "ltr") else ''
        b_lang = f' lang="{html.escape(block.language)}"' if block.language else ''
        style_attr = self._build_inline_style(block.style)
        content_escaped = html.escape(block.content)

        if block.blockType == "heading":
            lvl = block.level or 1
            return f'<h{lvl} id="{b_id}" data-block-id="{b_id}"{b_dir}{b_lang}{style_attr}>{content_escaped}</h{lvl}>'

        elif block.blockType == "paragraph":
            return f'<p id="{b_id}" data-block-id="{b_id}"{b_dir}{b_lang}{style_attr}>{content_escaped}</p>'

        elif block.blockType == "listItem":
            return f'<ul><li id="{b_id}" data-block-id="{b_id}"{b_dir}{b_lang}{style_attr}>{content_escaped}</li></ul>'

        elif block.blockType == "table" and block.tableData:
            t_style = ' style="width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: 15px;"'
            th_style = ' style="border: 1px solid #d1d5db; padding: 8px 12px; background-color: #f3f4f6; font-weight: bold; text-align: left;"'
            td_style = ' style="border: 1px solid #e5e7eb; padding: 8px 12px;"'

            parts = ['<div class="table-responsive">', f'  <table id="{b_id}" data-block-id="{b_id}"{t_style}>']
            if block.tableData.headers:
                parts.append('    <thead><tr>')
                for h in block.tableData.headers:
                    parts.append(f'      <th{th_style}>{html.escape(h.content)}</th>')
                parts.append('    </tr></thead>')
            if block.tableData.rows:
                parts.append('    <tbody>')
                for row in block.tableData.rows:
                    parts.append('      <tr>')
                    for cell in row.cells:
                        parts.append(f'        <td{td_style}>{html.escape(cell.content)}</td>')
                    parts.append('      </tr>')
                parts.append('    </tbody>')
            parts.append('  </table>')
            parts.append('</div>')
            return "\n".join(parts)

        elif block.blockType == "image" and block.imageData:
            img_src = self._resolve_image_src(
                block.imageData.src,
                doc_id,
                asset_base_url=asset_base_url,
                embed_images_base64=embed_images_base64,
                assets_dir=assets_dir
            )
            img_alt = html.escape(block.imageData.alt or "Figure")
            caption_html = (
                f'<figcaption style="font-size: 13px; color: #6b7280; margin-top: 6px; text-align: center; font-style: italic;">{html.escape(block.imageData.caption)}</figcaption>'
                if block.imageData.caption else ''
            )
            fig_style = ' style="margin: 1.5rem 0; text-align: center;"'
            
            w = block.imageData.width
            h = block.imageData.height
            if w and w < 600:
                img_style = f' style="width: {w}px; max-width: 100%; height: auto; border-radius: 4px; display: inline-block;"'
                dim_attrs = f' width="{w}"' + (f' height="{h}"' if h else '')
            else:
                img_style = ' style="max-width: 100%; height: auto; border-radius: 4px; display: inline-block;"'
                dim_attrs = ''

            return f'<figure id="{b_id}" data-block-id="{b_id}"{fig_style}>\n  <img src="{img_src}" alt="{img_alt}" loading="lazy"{dim_attrs}{img_style} />\n  {caption_html}\n</figure>'

        elif block.blockType == "equation":
            formula = html.escape(block.mathFormula or block.content)
            eq_style = ' style="font-family: monospace; font-size: 16px; padding: 12px; background-color: #f8fafc; border-radius: 6px; text-align: center; margin: 1rem 0;"'
            return f'<div class="math-equation" id="{b_id}" data-block-id="{b_id}"{eq_style}>{formula}</div>'

        elif block.blockType == "code":
            c_style = ' style="font-family: monospace; font-size: 14px; background-color: #1e293b; color: #f8fafc; padding: 12px; border-radius: 6px; overflow-x: auto;"'
            return f'<pre id="{b_id}" data-block-id="{b_id}"{c_style}><code>{content_escaped}</code></pre>'

        elif block.blockType == "blockquote":
            bq_style = ' style="border-left: 4px solid #10b981; padding-left: 1rem; margin: 1rem 0; color: #4b5563; font-style: italic;"'
            return f'<blockquote id="{b_id}" data-block-id="{b_id}"{bq_style}><p>{content_escaped}</p></blockquote>'

        elif block.blockType == "pageBreak":
            return f'<hr class="page-break" data-page-break="{block.sourcePage}" style="border: 0; border-top: 1px dashed #e5e7eb; margin: 2rem 0;" />'

        return f'<p id="{b_id}" data-block-id="{b_id}"{style_attr}>{content_escaped}</p>'

    def generate_page_snippet(
        self,
        doc: CanonicalDocument,
        page_num: int,
        asset_base_url: Optional[str] = None,
        embed_images_base64: bool = False,
        assets_dir: Optional[Path] = None
    ) -> str:
        """
        Generate EDITOR-READY HTML snippet for a specific PDF page.
        - HTML fragment only (<section data-page="N">...</section>)
        - No html/head/body wrappers, no JS
        - Inline CSS for direct copy/paste into UEducate or external rich text editors
        - Full Unicode preservation and real selectable text nodes
        """
        page_blocks = [b for b in doc.blocks if b.sourcePage == page_num]
        doc_dir = "rtl" if is_rtl(doc.language) else "ltr"
        doc_lang = html.escape(doc.language or "en")

        section_style = ' style="font-family: system-ui, -apple-system, sans-serif; font-size: 16px; line-height: 1.6; color: #1f2937;"'
        parts: List[str] = [
            f'<section data-page="{page_num}" class="ue-page" lang="{doc_lang}" dir="{doc_dir}"{section_style}>'
        ]

        for block in page_blocks:
            if block.blockType == "pageBreak":
                continue
            rendered = self.generate_block_html(
                block,
                doc_id=doc.documentId,
                asset_base_url=asset_base_url,
                embed_images_base64=embed_images_base64,
                assets_dir=assets_dir
            )
            parts.append(f'  {rendered}')

        parts.append('</section>')
        return "\n".join(parts)

    def generate_page_standalone(
        self,
        doc: CanonicalDocument,
        page_num: int,
        asset_base_url: Optional[str] = None,
        assets_dir: Optional[Path] = None
    ) -> str:
        """
        Generate complete STANDALONE HTML document for previewing or downloading a single page.
        """
        snippet = self.generate_page_snippet(
            doc,
            page_num,
            asset_base_url=asset_base_url,
            embed_images_base64=False,
            assets_dir=assets_dir
        )
        doc_dir = "rtl" if is_rtl(doc.language) else "ltr"
        doc_lang = html.escape(doc.language or "en")
        title = html.escape(f"{doc.title} - Page {page_num}")

        return f"""<!DOCTYPE html>
<html lang="{doc_lang}" dir="{doc_dir}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
{READER_CSS}
  </style>
</head>
<body>
  <div class="document-container">
{snippet}
  </div>
</body>
</html>"""

    def generate_html(
        self,
        doc: CanonicalDocument,
        standalone: bool = True,
        asset_base_url: Optional[str] = None,
        assets_dir: Optional[Path] = None,
        **kwargs
    ) -> str:
        """
        Generate full-document HTML with per-page sections and inline styles.
        """
        pages_dict: Dict[int, List[DocumentBlock]] = {}
        for block in doc.blocks:
            page = block.sourcePage or 1
            if page not in pages_dict:
                pages_dict[page] = []
            pages_dict[page].append(block)

        body_parts: List[str] = []
        doc_lang = html.escape(doc.language or "en")
        doc_dir = "rtl" if is_rtl(doc.language) else "ltr"
        body_parts.append(f'<article class="canonical-document" lang="{doc_lang}" dir="{doc_dir}" data-document-id="{html.escape(doc.documentId)}">')

        sorted_pages = sorted(pages_dict.keys())
        if not sorted_pages:
            sorted_pages = [1]

        for p_num in sorted_pages:
            snippet = self.generate_page_snippet(
                doc,
                p_num,
                asset_base_url=asset_base_url,
                embed_images_base64=False,
                assets_dir=assets_dir
            )
            body_parts.append(snippet)

        body_parts.append('</article>')
        inner_html = "\n".join(body_parts)

        if not standalone:
            return inner_html

        title_escaped = html.escape(doc.title or "Document")

        return f"""<!DOCTYPE html>
<html lang="{doc_lang}" dir="{doc_dir}">
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

    def generate_all_pages_bundle(
        self,
        doc: CanonicalDocument,
        doc_dir: Path,
        asset_base_url: Optional[str] = None
    ) -> None:
        """
        Generate independent page-by-page deliverables on disk.
        For each page:
          pages/{page_num:04d}/paste.html
          pages/{page_num:04d}/standalone.html
          pages/{page_num:04d}/metadata.json
        """
        pages_root = doc_dir / "pages"
        pages_root.mkdir(parents=True, exist_ok=True)
        assets_dir = doc_dir / "assets"

        page_meta_lookup = {p.pageNumber: p for p in doc.pages}
        page_numbers = sorted(set(b.sourcePage for b in doc.blocks if b.sourcePage > 0))
        if not page_numbers:
            page_numbers = list(range(1, max(1, doc.page_count) + 1))

        for p_num in page_numbers:
            page_folder = pages_root / f"{p_num:04d}"
            page_folder.mkdir(parents=True, exist_ok=True)

            # 1. Editor-Ready Paste HTML snippet (embeds self-contained base64 images for seamless external editor paste)
            paste_html = self.generate_page_snippet(
                doc,
                p_num,
                asset_base_url=asset_base_url,
                embed_images_base64=True,
                assets_dir=assets_dir
            )
            (page_folder / "paste.html").write_text(paste_html, encoding="utf-8")

            # 2. Standalone HTML Document
            standalone_html = self.generate_page_standalone(
                doc,
                p_num,
                asset_base_url=asset_base_url,
                assets_dir=assets_dir
            )
            (page_folder / "standalone.html").write_text(standalone_html, encoding="utf-8")

            # 3. Page Metadata JSON
            meta_obj = page_meta_lookup.get(p_num)
            page_meta_dict = meta_obj.model_dump() if meta_obj else {"pageNumber": p_num}
            (page_folder / "metadata.json").write_text(json.dumps(page_meta_dict, indent=2), encoding="utf-8")

html_generation_service = HTMLGenerationService()

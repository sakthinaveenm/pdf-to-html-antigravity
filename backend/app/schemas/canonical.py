"""
Pydantic v2 Canonical Document Model (Intermediate Representation AST).
Versioned, lossless document structure before rendering to HTML or feeding TipTap editor.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import hashlib

class InlineFormat(BaseModel):
    tag: str            # 'strong', 'em', 'code', 'link', 'sub', 'sup'
    start: int          # Codepoint offset in block content
    end: int            # Codepoint offset in block content
    href: Optional[str] = None
    title: Optional[str] = None

class TableCell(BaseModel):
    content: str
    is_header: bool = False
    rowspan: int = 1
    colspan: int = 1
    language: Optional[str] = None
    direction: Optional[str] = None

class TableRow(BaseModel):
    cells: List[TableCell] = Field(default_factory=list)

class TableData(BaseModel):
    headers: List[TableCell] = Field(default_factory=list)
    rows: List[TableRow] = Field(default_factory=list)
    caption: Optional[str] = None

class ImageData(BaseModel):
    asset_id: str
    src: str
    alt: str = ""
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: str = "image/png"

class BlockProvenance(BaseModel):
    engine: str               # 'marker', 'docling', 'ocr', 'native'
    page: int
    confidence: Optional[float] = None
    bbox: Optional[List[float]] = None  # [x0, y0, x1, y1] normalized or pts

class DocumentBlock(BaseModel):
    blockId: str              # Deterministic identifier, e.g. 'blk-p1-s001-a1b2'
    blockType: str            # heading, paragraph, list, listItem, table, image, caption, blockquote, equation, code, pageBreak
    sourcePage: int           # 1-based page index
    language: Optional[str] = None
    direction: str = "ltr"    # 'ltr', 'rtl', 'auto'
    content: str = ""         # Clean Unicode text content
    inlineFormatting: List[InlineFormat] = Field(default_factory=list)
    readingOrder: int = 0
    provenance: BlockProvenance
    level: Optional[int] = None           # For headings 1-6
    tableData: Optional[TableData] = None  # For table blocks
    imageData: Optional[ImageData] = None  # For image blocks
    mathFormula: Optional[str] = None     # For equation blocks (LaTeX/MathML)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def generate_block_id(cls, page: int, seq: int, text: str) -> str:
        """Create a stable deterministic block identifier."""
        snippet = (text or "").strip()[:40].encode("utf-8")
        h = hashlib.sha256(f"p{page}_s{seq}_".encode("utf-8") + snippet).hexdigest()[:6]
        return f"blk-p{page}-s{seq:03d}-{h}"

class PageMetadata(BaseModel):
    pageNumber: int
    width: float
    height: float
    rotation: int = 0
    classification: str       # DIGITAL_TEXT, SCANNED_IMAGE, MIXED_CONTENT, TEXT_ENCODING_PROBLEM, UNKNOWN
    language: Optional[str] = None
    detectedScript: Optional[str] = None
    textConfidence: Optional[float] = None
    hasImages: bool = False
    imageCount: int = 0

class AssetMetadata(BaseModel):
    assetId: str
    fileName: str
    mimeType: str
    relativePath: str
    byteSize: int
    page: int
    width: Optional[int] = None
    height: Optional[int] = None

class DocumentWarning(BaseModel):
    code: str
    message: str
    page: Optional[int] = None
    severity: str = "warning"  # info, warning, error

class CanonicalDocument(BaseModel):
    documentId: str
    sourceFileName: str
    sourceChecksum: str
    title: str
    language: str = "en"
    revision: int = 1
    pages: List[PageMetadata] = Field(default_factory=list)
    blocks: List[DocumentBlock] = Field(default_factory=list)
    assets: Dict[str, AssetMetadata] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[DocumentWarning] = Field(default_factory=list)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    def to_tiptap_json(self) -> Dict[str, Any]:
        """Convert CanonicalDocument AST to TipTap/ProseMirror schema nodes."""
        nodes: List[Dict[str, Any]] = []
        for block in self.blocks:
            if block.blockType == "heading":
                nodes.append({
                    "type": "heading",
                    "attrs": {"level": block.level or 1, "id": block.blockId, "data-block-id": block.blockId},
                    "content": [{"type": "text", "text": block.content}] if block.content else []
                })
            elif block.blockType == "paragraph":
                nodes.append({
                    "type": "paragraph",
                    "attrs": {"id": block.blockId, "data-block-id": block.blockId, "dir": block.direction},
                    "content": [{"type": "text", "text": block.content}] if block.content else []
                })
            elif block.blockType == "blockquote":
                nodes.append({
                    "type": "blockquote",
                    "attrs": {"data-block-id": block.blockId},
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": block.content}]
                    }]
                })
            elif block.blockType == "code":
                nodes.append({
                    "type": "codeBlock",
                    "attrs": {"data-block-id": block.blockId},
                    "content": [{"type": "text", "text": block.content}]
                })
            elif block.blockType == "image" and block.imageData:
                nodes.append({
                    "type": "image",
                    "attrs": {
                        "src": block.imageData.src,
                        "alt": block.imageData.alt,
                        "title": block.imageData.caption or "",
                        "data-block-id": block.blockId
                    }
                })
            elif block.blockType == "table" and block.tableData:
                table_rows = []
                if block.tableData.headers:
                    header_cells = [{
                        "type": "tableHeader",
                        "attrs": {"colspan": c.colspan, "rowspan": c.rowspan},
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": c.content}]}]
                    } for c in block.tableData.headers]
                    table_rows.append({"type": "tableRow", "content": header_cells})
                for row in block.tableData.rows:
                    row_cells = [{
                        "type": "tableCell",
                        "attrs": {"colspan": c.colspan, "rowspan": c.rowspan},
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": c.content}]}]
                    } for c in row.cells]
                    table_rows.append({"type": "tableRow", "content": row_cells})
                nodes.append({
                    "type": "table",
                    "attrs": {"data-block-id": block.blockId},
                    "content": table_rows
                })
            elif block.blockType == "pageBreak":
                nodes.append({
                    "type": "horizontalRule",
                    "attrs": {"data-page-break": block.sourcePage, "data-block-id": block.blockId}
                })
            else:
                nodes.append({
                    "type": "paragraph",
                    "attrs": {"data-block-id": block.blockId},
                    "content": [{"type": "text", "text": block.content}] if block.content else []
                })

        return {
            "type": "doc",
            "content": nodes
        }

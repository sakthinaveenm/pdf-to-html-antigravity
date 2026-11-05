"""
Docling Converter.
Wraps IBM Docling document parsing engine to convert complex multi-column
PDFs, tables, and academic papers into the Canonical Document Model AST.
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from backend.app.schemas.canonical import (
    CanonicalDocument, DocumentBlock, BlockProvenance, PageMetadata,
    AssetMetadata, TableData, TableRow, TableCell, DocumentWarning
)
from backend.app.services.converters.base import PDFConverter, ConversionOptions, ConverterCapabilities
from backend.app.constants.languages import detect_script_from_text, get_direction_for_script

class DoclingConverter(PDFConverter):
    def __init__(self):
        self._converter = None

    def check_availability(self) -> bool:
        try:
            import docling
            return True
        except ImportError:
            return False

    def get_capabilities(self) -> ConverterCapabilities:
        import docling
        return ConverterCapabilities(
            engine_name="DOCLING",
            is_available=True,
            version=getattr(docling, "__version__", "2.147.0"),
            supports_ocr=True,
            supports_tables=True,
            supports_equations=True,
            supports_gpu=True,
            notes="IBM Docling rich document structure & table extraction"
        )

    def _get_converter(self):
        if self._converter is None:
            from docling.document_converter import DocumentConverter
            self._converter = DocumentConverter()
        return self._converter

    def convert(self, source_path: Path, options: ConversionOptions) -> CanonicalDocument:
        converter = self._get_converter()
        doc_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        
        # Execute docling conversion
        result = converter.convert(source_path)
        doc = result.document

        pages_meta: List[PageMetadata] = []
        all_blocks: List[DocumentBlock] = []
        assets_dict: Dict[str, AssetMetadata] = {}
        warnings: List[DocumentWarning] = []

        total_pages = doc.num_pages() if hasattr(doc, "num_pages") else 1
        for p in range(1, total_pages + 1):
            pages_meta.append(PageMetadata(
                pageNumber=p,
                width=612.0,
                height=792.0,
                classification="DIGITAL_TEXT"
            ))

        # Export HTML and parse elements cleanly to canonical AST
        html_content = doc.export_to_html()
        soup = BeautifulSoup(html_content, "html.parser")

        reading_order = 0
        current_page = 1

        # Walk through top level body elements
        body = soup.find("body") or soup
        for elem in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "table", "pre", "figure", "blockquote"], recursive=True):
            reading_order += 1
            tag = elem.name.lower()
            text = elem.get_text().strip()

            script = detect_script_from_text(text) if text else "latin"
            direction = get_direction_for_script(script)

            if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(tag[1])
                block_id = DocumentBlock.generate_block_id(current_page, reading_order, text)
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="heading",
                    sourcePage=current_page,
                    language=script,
                    direction=direction,
                    content=text,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="docling", page=current_page),
                    level=level
                ))
            elif tag == "p":
                if not text:
                    continue
                block_id = DocumentBlock.generate_block_id(current_page, reading_order, text)
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="paragraph",
                    sourcePage=current_page,
                    language=script,
                    direction=direction,
                    content=text,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="docling", page=current_page)
                ))
            elif tag == "table":
                t_headers: List[TableCell] = []
                t_rows: List[TableRow] = []
                
                # Check header cells
                for th in elem.find_all("th"):
                    t_headers.append(TableCell(content=th.get_text().strip(), is_header=True))
                
                # Check rows
                for tr in elem.find_all("tr"):
                    cells = []
                    for td in tr.find_all(["td", "th"]):
                        is_h = td.name == "th"
                        cells.append(TableCell(content=td.get_text().strip(), is_header=is_h))
                    if cells:
                        t_rows.append(TableRow(cells=cells))

                block_id = DocumentBlock.generate_block_id(current_page, reading_order, "table")
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="table",
                    sourcePage=current_page,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="docling", page=current_page),
                    tableData=TableData(headers=t_headers, rows=t_rows)
                ))
            elif tag == "pre":
                block_id = DocumentBlock.generate_block_id(current_page, reading_order, text)
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="code",
                    sourcePage=current_page,
                    content=text,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="docling", page=current_page)
                ))
            elif tag == "blockquote":
                block_id = DocumentBlock.generate_block_id(current_page, reading_order, text)
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="blockquote",
                    sourcePage=current_page,
                    content=text,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="docling", page=current_page)
                ))

        return CanonicalDocument(
            documentId=options.document_id,
            sourceFileName=source_path.name,
            sourceChecksum=doc_sha,
            title=source_path.stem,
            language=pages_meta[0].detectedScript if pages_meta else "en",
            revision=1,
            pages=pages_meta,
            blocks=all_blocks,
            assets=assets_dict,
            metadata={"engine": "docling", "total_blocks": len(all_blocks)},
            warnings=warnings
        )


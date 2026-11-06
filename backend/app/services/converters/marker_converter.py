"""
Marker PDF Converter.
Wraps VikParuchuri's Marker layout and parsing pipeline (Surya layout/OCR)
with lazy model initialization and memory shutdown.
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import markdown2

from backend.app.schemas.canonical import (
    CanonicalDocument, DocumentBlock, BlockProvenance, PageMetadata,
    AssetMetadata, TableData, TableRow, TableCell, DocumentWarning
)
from backend.app.services.converters.base import PDFConverter, ConversionOptions, ConverterCapabilities
from backend.app.constants.languages import (
    detect_script_from_text, get_direction_for_script, resolve_document_language
)

class MarkerConverter(PDFConverter):
    def __init__(self):
        self._model_dict = None

    def check_availability(self) -> bool:
        try:
            import marker
            return True
        except ImportError:
            return False

    def get_capabilities(self) -> ConverterCapabilities:
        import marker
        return ConverterCapabilities(
            engine_name="MARKER",
            is_available=True,
            version=getattr(marker, "__version__", "2.1.0"),
            supports_ocr=True,
            supports_tables=True,
            supports_equations=True,
            supports_gpu=True,
            notes="Marker Surya layout models with markdown/HTML generation"
        )

    def _load_models(self):
        if self._model_dict is None:
            from marker.models import create_model_dict
            self._model_dict = create_model_dict()
        return self._model_dict

    def unload_models(self):
        if self._model_dict is not None:
            try:
                from marker.models import shutdown_models
                shutdown_models()
            except Exception:
                pass
            self._model_dict = None

    def convert(self, source_path: Path, options: ConversionOptions) -> CanonicalDocument:
        from marker.converters.pdf import PdfConverter
        from marker.output import text_from_rendered
        
        doc_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        model_dict = self._load_models()
        converter = PdfConverter(artifact_dict=model_dict)
        
        rendered = converter(str(source_path))
        full_text, _, images = text_from_rendered(rendered)
        
        # Save images
        assets_dict: Dict[str, AssetMetadata] = {}
        if images:
            for img_name, img_obj in images.items():
                img_path = options.assets_dir / img_name
                img_obj.save(str(img_path))
                assets_dict[img_name] = AssetMetadata(
                    assetId=img_name,
                    fileName=img_name,
                    mimeType="image/png",
                    relativePath=f"assets/{img_name}",
                    byteSize=img_path.stat().st_size,
                    page=1
                )

        # Convert markdown output to HTML then parse into blocks
        html = markdown2.markdown(full_text, extras=["tables", "fenced-code-blocks", "footnotes"])
        soup = BeautifulSoup(html, "html.parser")

        pages_meta = [PageMetadata(pageNumber=1, width=612.0, height=792.0, classification="DIGITAL_TEXT")]
        all_blocks: List[DocumentBlock] = []
        reading_order = 0

        for elem in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "table", "pre", "blockquote"]):
            reading_order += 1
            tag = elem.name.lower()
            text = elem.get_text().strip()
            script = detect_script_from_text(text) if text else "latin"
            direction = get_direction_for_script(script)

            if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(tag[1])
                block_id = DocumentBlock.generate_block_id(1, reading_order, text)
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="heading",
                    sourcePage=1,
                    language=script,
                    direction=direction,
                    content=text,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="marker", page=1),
                    level=level
                ))
            elif tag == "p":
                if not text:
                    continue
                block_id = DocumentBlock.generate_block_id(1, reading_order, text)
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="paragraph",
                    sourcePage=1,
                    language=script,
                    direction=direction,
                    content=text,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="marker", page=1)
                ))
            elif tag == "table":
                t_headers = [TableCell(content=th.get_text().strip(), is_header=True) for th in elem.find_all("th")]
                t_rows = []
                for tr in elem.find_all("tr"):
                    cells = [TableCell(content=td.get_text().strip(), is_header=td.name=="th") for td in tr.find_all(["td", "th"])]
                    if cells:
                        t_rows.append(TableRow(cells=cells))
                block_id = DocumentBlock.generate_block_id(1, reading_order, "table")
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="table",
                    sourcePage=1,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="marker", page=1),
                    tableData=TableData(headers=t_headers, rows=t_rows)
                ))
            elif tag == "pre":
                block_id = DocumentBlock.generate_block_id(1, reading_order, text)
                all_blocks.append(DocumentBlock(
                    blockId=block_id,
                    blockType="code",
                    sourcePage=1,
                    content=text,
                    readingOrder=reading_order,
                    provenance=BlockProvenance(engine="marker", page=1)
                ))

        # Determine overall dominant script across all content blocks
        script_counts: Dict[str, int] = {}
        for b in all_blocks:
            if b.language and b.language != "latin":
                script_counts[b.language] = script_counts.get(b.language, 0) + 1
        
        dominant_script = (
            max(script_counts.items(), key=lambda x: x[1])[0]
            if script_counts
            else (pages_meta[0].detectedScript if pages_meta else "latin")
        )
        resolved_lang = resolve_document_language(options.document_language, dominant_script)

        return CanonicalDocument(
            documentId=options.document_id,
            sourceFileName=source_path.name,
            sourceChecksum=doc_sha,
            title=source_path.stem,
            language=resolved_lang,
            revision=1,
            pages=pages_meta,
            blocks=all_blocks,
            assets=assets_dict,
            metadata={"engine": "marker", "total_blocks": len(all_blocks), "dominant_script": dominant_script},
            warnings=[]
        )


"""
Native Hybrid PDF Converter.
High-precision, local-first engine using PyMuPDF (fitz) text and table extraction,
embedded raster image dumping, and Tesseract OCR for scanned/mixed pages.
Always available, runs efficiently on CPU with zero remote dependencies.
"""
import io
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf as fitz
from PIL import Image

from backend.app.schemas.canonical import (
    CanonicalDocument, DocumentBlock, BlockProvenance, InlineFormat,
    PageMetadata, AssetMetadata, TableData, TableRow, TableCell,
    ImageData, DocumentWarning
)
from backend.app.services.converters.base import PDFConverter, ConversionOptions, ConverterCapabilities
from backend.app.services.ocr.tesseract_service import ocr_service
from backend.app.services.ocr.legacy_indic_decoder import (
    decode_chanakya_to_unicode, is_legacy_indic_font, detect_legacy_indic_text
)
from backend.app.constants.statuses import PageClassification
from backend.app.constants.languages import (
    detect_script_from_text, get_direction_for_script, resolve_document_language,
    get_tesseract_langs_for_scripts, is_rtl
)

class NativeHybridConverter(PDFConverter):
    def check_availability(self) -> bool:
        return True

    def get_capabilities(self) -> ConverterCapabilities:
        return ConverterCapabilities(
            engine_name="NATIVE",
            is_available=True,
            version=fitz.__version__,
            supports_ocr=True,
            supports_tables=True,
            supports_equations=True,
            supports_gpu=False,
            notes="Zero-dependency local hybrid engine using PyMuPDF and Tesseract"
        )

    def convert(self, source_path: Path, options: ConversionOptions) -> CanonicalDocument:
        doc = fitz.open(str(source_path))
        doc_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
        options.assets_dir.mkdir(parents=True, exist_ok=True)

        pages_meta: List[PageMetadata] = []
        all_blocks: List[DocumentBlock] = []
        assets_dict: Dict[str, AssetMetadata] = {}
        warnings: List[DocumentWarning] = []

        total_pages = len(doc)
        if options.max_pages:
            total_pages = min(total_pages, options.max_pages)

        # First pass: collect font statistics for heading detection
        font_sizes: List[float] = []
        for p_idx in range(total_pages):
            page = doc[p_idx]
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                if block.get("type") == 0:  # text
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            size = span.get("size", 12.0)
                            if span.get("text", "").strip():
                                font_sizes.append(size)

        median_font_size = 11.0
        if font_sizes:
            font_sizes.sort()
            median_font_size = font_sizes[len(font_sizes) // 2]

        reading_order_counter = 0

        for p_idx in range(total_pages):
            page_num = p_idx + 1
            page = doc[p_idx]
            rect = page.rect
            text_raw = page.get_text("text") or ""
            images_on_page = page.get_images(full=True)
            image_count = len(images_on_page)

            # Check for legacy non-Unicode Indic fonts or text (Chanakya, KrutiDev, etc.)
            page_fonts = [f[3] for f in page.get_fonts() if len(f) > 3]
            has_legacy_indic = any(is_legacy_indic_font(fn) for fn in page_fonts)
            has_legacy_text, _ = detect_legacy_indic_text(text_raw)
            is_legacy_indic = has_legacy_indic or has_legacy_text

            # Classify page
            char_count = len(text_raw.strip())
            is_scanned = (
                (char_count < 30 and (image_count > 0 or options.force_ocr))
                or options.force_ocr
            )

            classification = (
                PageClassification.TEXT_ENCODING_PROBLEM if is_legacy_indic
                else (PageClassification.SCANNED_IMAGE if is_scanned
                else (PageClassification.MIXED_CONTENT if image_count > 0 else PageClassification.DIGITAL_TEXT))
            )

            # Detect dominant script on page
            if is_legacy_indic:
                page_script = "devanagari"
            else:
                page_script = detect_script_from_text(text_raw) if text_raw else "latin"
            page_direction = get_direction_for_script(page_script)

            pages_meta.append(PageMetadata(
                pageNumber=page_num,
                width=rect.width,
                height=rect.height,
                rotation=page.rotation,
                classification=classification.value,
                detectedScript=page_script,
                hasImages=image_count > 0,
                imageCount=image_count
            ))

            # 1. Extract Tables on this page
            table_bboxes = []
            try:
                tables = page.find_tables()
                for t_idx, table in enumerate(tables):
                    table_bboxes.append(table.bbox)
                    t_headers: List[TableCell] = []
                    t_rows: List[TableRow] = []

                    extracted_data = table.extract()
                    if extracted_data and len(extracted_data) > 0:
                        first_row = extracted_data[0]
                        for cell_text in first_row:
                            t_headers.append(TableCell(content=str(cell_text or "").strip(), is_header=True))
                        for r in extracted_data[1:]:
                            cells = [TableCell(content=str(c or "").strip(), is_header=False) for c in r]
                            t_rows.append(TableRow(cells=cells))

                    reading_order_counter += 1
                    block_id = DocumentBlock.generate_block_id(page_num, reading_order_counter, "table")
                    all_blocks.append(DocumentBlock(
                        blockId=block_id,
                        blockType="table",
                        sourcePage=page_num,
                        readingOrder=reading_order_counter,
                        provenance=BlockProvenance(engine="native", page=page_num, bbox=list(table.bbox)),
                        tableData=TableData(headers=t_headers, rows=t_rows)
                    ))
            except Exception as e:
                warnings.append(DocumentWarning(
                    code="TABLE_EXTRACTION_ERROR",
                    message=f"Failed to extract table on page {page_num}: {str(e)}",
                    page=page_num
                ))

            # 2. Extract Embedded Images
            for img_idx, img_info in enumerate(images_on_page):
                try:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image.get("ext", "png")
                        asset_id = f"img_p{page_num}_{img_idx}_{xref}"
                        asset_filename = f"{asset_id}.{image_ext}"
                        asset_path = options.assets_dir / asset_filename
                        asset_path.write_bytes(image_bytes)

                        asset_meta = AssetMetadata(
                            assetId=asset_id,
                            fileName=asset_filename,
                            mimeType=f"image/{image_ext}",
                            relativePath=f"assets/{asset_filename}",
                            byteSize=len(image_bytes),
                            page=page_num,
                            width=base_image.get("width"),
                            height=base_image.get("height")
                        )
                        assets_dict[asset_id] = asset_meta

                        # Add image block only if significant size (> 30x30 px to skip 1px lines/spacers)
                        if (base_image.get("width", 0) > 30 and base_image.get("height", 0) > 30):
                            reading_order_counter += 1
                            block_id = DocumentBlock.generate_block_id(page_num, reading_order_counter, asset_id)
                            all_blocks.append(DocumentBlock(
                                blockId=block_id,
                                blockType="image",
                                sourcePage=page_num,
                                readingOrder=reading_order_counter,
                                provenance=BlockProvenance(engine="native", page=page_num),
                                imageData=ImageData(
                                    asset_id=asset_id,
                                    src=f"/api/v1/documents/{options.document_id}/assets/{asset_filename}" if options.document_id else f"./assets/{asset_filename}",
                                    alt=f"Figure on page {page_num}",
                                    width=base_image.get("width"),
                                    height=base_image.get("height")
                                )
                            ))
                except Exception as e:
                    warnings.append(DocumentWarning(
                        code="IMAGE_EXTRACTION_ERROR",
                        message=f"Failed to extract image on page {page_num}: {str(e)}",
                        page=page_num
                    ))

            # 3. Process Text Content
            if is_scanned:
                # If OCR languages is AUTO or empty, dynamically detect or fallback
                ocr_langs = options.ocr_languages
                if not ocr_langs or ocr_langs.strip().upper() == "AUTO":
                    if is_legacy_indic:
                        ocr_langs = "hin+eng"
                    elif page_script and page_script != "latin":
                        ocr_langs = get_tesseract_langs_for_scripts([page_script])
                    else:
                        ocr_langs = "eng"
                elif is_legacy_indic and "hin" not in ocr_langs:
                    ocr_langs = f"hin+{ocr_langs}"

                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_res = ocr_service.ocr_image(img, languages=ocr_langs, detected_scripts=[page_script])
                
                ocr_text = ocr_res.text.strip() if ocr_res.text else ""
                
                if ocr_text:
                    paragraphs = [p.strip() for p in ocr_text.split("\n\n") if p.strip()]
                    for p_text in paragraphs:
                        reading_order_counter += 1
                        block_id = DocumentBlock.generate_block_id(page_num, reading_order_counter, p_text)
                        script = detect_script_from_text(p_text)
                        direction = get_direction_for_script(script)
                        all_blocks.append(DocumentBlock(
                            blockId=block_id,
                            blockType="paragraph",
                            sourcePage=page_num,
                            language=script,
                            direction=direction,
                            content=p_text,
                            readingOrder=reading_order_counter,
                            provenance=BlockProvenance(engine="ocr", page=page_num, confidence=ocr_res.confidence)
                        ))
                elif is_legacy_indic and text_raw:
                    # Fallback to direct Chanakya/KrutiDev decoding of digital text
                    decoded_text = decode_chanakya_to_unicode(text_raw)
                    paragraphs = [p.strip() for p in decoded_text.split("\n\n") if p.strip()]
                    for p_text in paragraphs:
                        reading_order_counter += 1
                        block_id = DocumentBlock.generate_block_id(page_num, reading_order_counter, p_text)
                        all_blocks.append(DocumentBlock(
                            blockId=block_id,
                            blockType="paragraph",
                            sourcePage=page_num,
                            language="devanagari",
                            direction="ltr",
                            content=p_text,
                            readingOrder=reading_order_counter,
                            provenance=BlockProvenance(engine="legacy_indic_decoder", page=page_num, confidence=0.92)
                        ))
                else:
                    warnings.append(DocumentWarning(
                        code="OCR_NO_TEXT",
                        message=f"OCR yielded no text for scanned page {page_num}.",
                        page=page_num
                    ))
            else:
                # Digital text: Parse blocks, lines, spans with geometry and font styling
                text_dict = page.get_text("dict")
                raw_blocks = text_dict.get("blocks", [])

                # Sort blocks primarily by vertical position (Y) and horizontal (X) for reading order
                raw_blocks.sort(key=lambda b: (round(b.get("bbox", [0,0,0,0])[1], -1), b.get("bbox", [0,0,0,0])[0]))

                for b in raw_blocks:
                    if b.get("type") != 0:  # Skip image blocks (already extracted above)
                        continue
                    
                    bbox = b.get("bbox", [0, 0, 0, 0])
                    # Check if this block falls inside an extracted table to avoid duplicate text
                    in_table = any(
                        (bbox[0] >= tb[0] - 2 and bbox[1] >= tb[1] - 2 and bbox[2] <= tb[2] + 2 and bbox[3] <= tb[3] + 2)
                        for tb in table_bboxes
                    )
                    if in_table:
                        continue

                    block_text_parts: List[str] = []
                    inline_formats: List[InlineFormat] = []
                    max_span_size = 0.0
                    is_bold_heading = False

                    current_offset = 0
                    for line in b.get("lines", []):
                        line_parts = []
                        for span in line.get("spans", []):
                            span_text = span.get("text", "")
                            if not span_text:
                                continue
                            if is_legacy_indic:
                                span_text = decode_chanakya_to_unicode(span_text)
                            
                            span_len = len(span_text)
                            span_size = span.get("size", 12.0)
                            font_flags = span.get("flags", 0)
                            font_name = span.get("font", "").lower()
                            
                            is_bold = (font_flags & 16 != 0) or ("bold" in font_name) or ("black" in font_name)
                            is_italic = (font_flags & 2 != 0) or ("italic" in font_name) or ("oblique" in font_name)
                            
                            if span_size > max_span_size:
                                max_span_size = span_size
                            if is_bold:
                                is_bold_heading = True

                            # Record inline formatting
                            if is_bold:
                                inline_formats.append(InlineFormat(
                                    tag="strong",
                                    start=current_offset,
                                    end=current_offset + span_len
                                ))
                            if is_italic:
                                inline_formats.append(InlineFormat(
                                    tag="em",
                                    start=current_offset,
                                    end=current_offset + span_len
                                ))

                            line_parts.append(span_text)
                            current_offset += span_len

                        block_text_parts.append(" ".join(line_parts))

                    full_text = " ".join([p.strip() for p in block_text_parts if p.strip()])
                    if not full_text:
                        continue

                    script = detect_script_from_text(full_text)
                    direction = get_direction_for_script(script)

                    # Normalize RTL / Arabic visual stream ordering to logical reading order
                    if direction == "rtl" or script == "arabic":
                        try:
                            from bidi.algorithm import get_display
                            full_text = get_display(full_text)
                        except Exception:
                            pass

                    # Determine block type: heading vs paragraph vs equation vs list item
                    block_type = "paragraph"
                    level = None

                    # Heading heuristics
                    ratio = max_span_size / max(1.0, median_font_size)
                    if ratio >= 1.7:
                        block_type = "heading"
                        level = 1
                    elif ratio >= 1.4:
                        block_type = "heading"
                        level = 2
                    elif ratio >= 1.2 or (is_bold_heading and len(full_text) < 80 and not full_text.endswith(".")):
                        block_type = "heading"
                        level = 3
                    elif full_text.startswith(("- ", "• ", "* ")) or (len(full_text) > 2 and full_text[0].isdigit() and full_text[1:3] in (". ", ") ")):
                        block_type = "listItem"
                    elif (full_text.startswith("$$") and full_text.endswith("$$")) or full_text.startswith(("\\begin{equation}", "\\begin{align}")):
                        block_type = "equation"

                    reading_order_counter += 1
                    block_id = DocumentBlock.generate_block_id(page_num, reading_order_counter, full_text)
                    
                    all_blocks.append(DocumentBlock(
                        blockId=block_id,
                        blockType=block_type,
                        sourcePage=page_num,
                        language=script,
                        direction=direction,
                        content=full_text,
                        inlineFormatting=inline_formats,
                        readingOrder=reading_order_counter,
                        provenance=BlockProvenance(engine="native", page=page_num, bbox=list(bbox)),
                        level=level,
                        mathFormula=full_text if block_type == "equation" else None
                    ))

            # Insert page break block between pages
            if page_num < total_pages:
                reading_order_counter += 1
                pb_id = f"pb-p{page_num}"
                all_blocks.append(DocumentBlock(
                    blockId=pb_id,
                    blockType="pageBreak",
                    sourcePage=page_num,
                    readingOrder=reading_order_counter,
                    provenance=BlockProvenance(engine="native", page=page_num)
                ))

        doc.close()

        title = doc.metadata.get("title") if hasattr(doc, "metadata") and doc.metadata else source_path.stem
        if not title or title.strip() == "":
            title = source_path.stem

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
            title=title,
            language=resolved_lang,
            revision=1,
            pages=pages_meta,
            blocks=all_blocks,
            assets=assets_dict,
            metadata={"total_blocks": len(all_blocks), "median_font_size": median_font_size, "dominant_script": dominant_script},
            warnings=warnings
        )

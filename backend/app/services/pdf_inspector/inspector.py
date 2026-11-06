"""
PDF Inspection Engine.
Deeply inspects PDF geometry, embedded fonts, text streams, image coverage,
Unicode integrity, and page classification (DIGITAL_TEXT, SCANNED_IMAGE,
MIXED_CONTENT, TEXT_ENCODING_PROBLEM, UNKNOWN).
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pymupdf as fitz
from pydantic import BaseModel
from backend.app.constants.statuses import PageClassification
from backend.app.constants.languages import detect_script_from_text, TARGET_LANGUAGES
from backend.app.services.ocr.legacy_indic_decoder import is_legacy_indic_font, detect_legacy_indic_text

class PageInspection(BaseModel):
    page_number: int
    width: float
    height: float
    rotation: int
    classification: PageClassification
    text_char_count: int
    text_word_count: int
    image_count: int
    image_area_ratio: float
    replacement_char_count: int
    suspicious_encoding: bool
    detected_script: str
    warnings: List[str]

class DocumentInspectionReport(BaseModel):
    is_valid_pdf: bool
    page_count: int
    title: str
    author: str
    creator: str
    producer: str
    encrypted: bool
    total_images: int
    overall_classification: PageClassification
    recommended_converter: str
    recommended_ocr_languages: List[str]
    pages: List[PageInspection]
    warnings: List[str]

class PDFInspectionService:
    def __init__(self):
        # Suspicious mojibake / repeated sequences regex
        self.repeated_noise_regex = re.compile(r'([a-zA-Z0-9\ufffd])\1{5,}')
        self.replacement_char = '\ufffd'

    def inspect(self, pdf_path: Path) -> DocumentInspectionReport:
        if not pdf_path.exists():
            return DocumentInspectionReport(
                is_valid_pdf=False,
                page_count=0,
                title="",
                author="",
                creator="",
                producer="",
                encrypted=False,
                total_images=0,
                overall_classification=PageClassification.UNKNOWN,
                recommended_converter="NATIVE",
                recommended_ocr_languages=["eng"],
                pages=[],
                warnings=["File does not exist on disk."]
            )

        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            return DocumentInspectionReport(
                is_valid_pdf=False,
                page_count=0,
                title="",
                author="",
                creator="",
                producer="",
                encrypted=False,
                total_images=0,
                overall_classification=PageClassification.UNKNOWN,
                recommended_converter="NATIVE",
                recommended_ocr_languages=["eng"],
                pages=[],
                warnings=[f"Failed to open PDF: {str(e)}"]
            )

        meta = doc.metadata or {}
        title = meta.get("title") or pdf_path.stem
        author = meta.get("author") or ""
        creator = meta.get("creator") or ""
        producer = meta.get("producer") or ""
        encrypted = doc.is_encrypted

        if encrypted:
            doc.close()
            return DocumentInspectionReport(
                is_valid_pdf=True,
                page_count=0,
                title=title,
                author=author,
                creator=creator,
                producer=producer,
                encrypted=True,
                total_images=0,
                overall_classification=PageClassification.UNKNOWN,
                recommended_converter="NATIVE",
                recommended_ocr_languages=["eng"],
                pages=[],
                warnings=["Document is password protected or encrypted."]
            )

        pages_inspection: List[PageInspection] = []
        doc_warnings: List[str] = []
        total_images = 0
        detected_scripts = set()
        scanned_count = 0
        digital_count = 0
        encoding_problem_count = 0

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            rect = page.rect
            page_area = max(1.0, rect.width * rect.height)
            
            # Extract text & characters
            text = page.get_text("text") or ""
            words = text.split()
            char_count = len(text)
            word_count = len(words)
            
            # Check replacement characters and suspicious encodings
            repl_count = text.count(self.replacement_char)
            suspicious = False
            page_warnings: List[str] = []

            if repl_count > 0:
                suspicious = True
                page_warnings.append(f"Contains {repl_count} Unicode replacement characters.")

            if self.repeated_noise_regex.search(text):
                suspicious = True
                page_warnings.append("Suspicious repeated glyph patterns detected (possible corrupt font mapping).")

            # Check image coverage
            images = page.get_images(full=True)
            image_count = len(images)
            total_images += image_count
            
            # Compute approximate image area coverage
            total_img_area = 0.0
            for img_info in images:
                try:
                    xref = img_info[0]
                    # Get bbox of image instances on page
                    for bbox in page.get_image_rects(xref):
                        total_img_area += max(0.0, bbox.width * bbox.height)
                except Exception:
                    pass
            
            image_area_ratio = min(1.0, total_img_area / page_area)

            # Check fonts for legacy non-Unicode Indic fonts (Chanakya, KrutiDev, DevLys, etc.)
            page_fonts = [f[3] for f in page.get_fonts() if len(f) > 3]
            has_legacy_indic_font = any(is_legacy_indic_font(fn) for fn in page_fonts)
            has_legacy_indic_text, _ = detect_legacy_indic_text(text)

            # Detect script
            script = detect_script_from_text(text)
            if has_legacy_indic_font or has_legacy_indic_text:
                script = "devanagari"
                suspicious = True
                page_warnings.append("Legacy non-Unicode Indic font (Walkman-Chanakya / KrutiDev) detected. Restoring Hindi Unicode text via OCR / legacy decoding.")

            detected_scripts.add(script)

            # Classify page
            classification: PageClassification
            if has_legacy_indic_font or has_legacy_indic_text:
                classification = PageClassification.TEXT_ENCODING_PROBLEM
                encoding_problem_count += 1
            elif suspicious and char_count > 10 and repl_count / max(1, char_count) > 0.15:
                classification = PageClassification.TEXT_ENCODING_PROBLEM
                encoding_problem_count += 1
            elif char_count < 30 and (image_count > 0 or image_area_ratio > 0.5):
                classification = PageClassification.SCANNED_IMAGE
                scanned_count += 1
            elif char_count >= 30 and image_area_ratio > 0.25:
                classification = PageClassification.MIXED_CONTENT
                digital_count += 1
            elif char_count >= 30:
                classification = PageClassification.DIGITAL_TEXT
                digital_count += 1
            else:
                classification = PageClassification.UNKNOWN
                page_warnings.append("Low text content and low image coverage.")

            pages_inspection.append(PageInspection(
                page_number=page_num,
                width=round(rect.width, 2),
                height=round(rect.height, 2),
                rotation=page.rotation,
                classification=classification,
                text_char_count=char_count,
                text_word_count=word_count,
                image_count=image_count,
                image_area_ratio=round(image_area_ratio, 3),
                replacement_char_count=repl_count,
                suspicious_encoding=suspicious,
                detected_script=script,
                warnings=page_warnings
            ))

        doc.close()

        # Overall classification
        total_p = len(pages_inspection)
        if total_p == 0:
            overall = PageClassification.UNKNOWN
        elif scanned_count == total_p:
            overall = PageClassification.SCANNED_IMAGE
        elif encoding_problem_count > 0:
            overall = PageClassification.TEXT_ENCODING_PROBLEM
        elif scanned_count > 0:
            overall = PageClassification.MIXED_CONTENT
        else:
            overall = PageClassification.DIGITAL_TEXT

        # Recommended converter
        if overall in (PageClassification.SCANNED_IMAGE, PageClassification.TEXT_ENCODING_PROBLEM):
            recommended_conv = "NATIVE"  # High precision OCR pipeline
        else:
            recommended_conv = "AUTO"

        # Recommended OCR languages
        ocr_langs = ["eng"]
        for s in detected_scripts:
            if s == "tamil":
                ocr_langs.append("tam")
            elif s == "devanagari":
                ocr_langs.append("hin")
            elif s == "telugu":
                ocr_langs.append("tel")
            elif s == "malayalam":
                ocr_langs.append("mal")
            elif s == "kannada":
                ocr_langs.append("kan")
            elif s == "bengali":
                ocr_langs.append("ben")
            elif s == "arabic":
                ocr_langs.append("ara")
            elif s == "cjk":
                ocr_langs.append("chi_sim")

        return DocumentInspectionReport(
            is_valid_pdf=True,
            page_count=total_p,
            title=title,
            author=author,
            creator=creator,
            producer=producer,
            encrypted=False,
            total_images=total_images,
            overall_classification=overall,
            recommended_converter=recommended_conv,
            recommended_ocr_languages=list(dict.fromkeys(ocr_langs)),
            pages=pages_inspection,
            warnings=doc_warnings
        )


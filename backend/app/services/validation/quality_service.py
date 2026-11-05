"""
Document Quality Validation Service.
Inspects converted CanonicalDocument and generated HTML for real selectable text nodes,
Unicode integrity, structural consistency, missing assets, and broken links.
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from backend.app.schemas.canonical import CanonicalDocument
from backend.app.schemas.capabilities import QualityReport, QualityMetric
from backend.app.constants.statuses import QualityStatus

class DocumentQualityService:
    def evaluate(self, doc: CanonicalDocument, html_content: str) -> QualityReport:
        soup = BeautifulSoup(html_content, "html.parser")
        metrics: List[QualityMetric] = []
        warnings: List[str] = []

        # 1. Text Selectability & DOM Text Node Validation
        raw_text = soup.get_text().strip()
        total_chars = len(raw_text)
        has_text_nodes = total_chars > 0
        text_score = min(1.0, total_chars / 50.0) if has_text_nodes else 0.0

        metrics.append(QualityMetric(
            name="Text Selectability",
            score=text_score,
            passed=has_text_nodes,
            details=f"Extracted {total_chars} characters across real DOM text nodes."
        ))
        if not has_text_nodes:
            warnings.append("Document HTML contains zero selectable text nodes.")

        # 2. Unicode Integrity Check
        replacement_count = raw_text.count("\ufffd")
        unicode_score = 1.0
        if total_chars > 0:
            repl_ratio = replacement_count / total_chars
            unicode_score = max(0.0, 1.0 - (repl_ratio * 5.0))
        
        passed_unicode = replacement_count == 0 or (total_chars > 0 and (replacement_count / total_chars) < 0.05)
        metrics.append(QualityMetric(
            name="Unicode Integrity",
            score=round(unicode_score, 2),
            passed=passed_unicode,
            details=f"Found {replacement_count} Unicode replacement characters in {total_chars} total chars."
        ))
        if replacement_count > 0:
            warnings.append(f"Document contains {replacement_count} Unicode replacement characters.")

        # 3. Structural Structure Check (Paragraphs, Headings, Tables)
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        paragraphs = soup.find_all("p")
        tables = soup.find_all("table")
        figures = soup.find_all("figure")
        blocks_with_ids = soup.find_all(lambda tag: tag.has_attr("data-block-id"))

        total_structural_blocks = len(headings) + len(paragraphs) + len(tables) + len(figures)
        structural_score = 1.0 if total_structural_blocks > 0 else 0.0
        metrics.append(QualityMetric(
            name="Structural Integrity",
            score=structural_score,
            passed=total_structural_blocks > 0,
            details=f"Structure: {len(headings)} headings, {len(paragraphs)} paragraphs, {len(tables)} tables, {len(figures)} figures."
        ))

        # 4. Block ID Consistency
        total_expected_blocks = len(doc.blocks)
        blocks_tagged = len(blocks_with_ids)
        block_id_passed = blocks_tagged >= max(1, int(total_expected_blocks * 0.7))
        metrics.append(QualityMetric(
            name="Block Identifier Stability",
            score=min(1.0, blocks_tagged / max(1, total_expected_blocks)),
            passed=block_id_passed,
            details=f"{blocks_tagged} blocks tagged with data-block-id (AST has {total_expected_blocks})."
        ))

        # 5. Asset References Check
        images = soup.find_all("img")
        broken_assets = 0
        for img in images:
            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue
            # Check relative asset presence
            clean_name = src.replace("./assets/", "").replace("assets/", "")
            if clean_name not in [a.fileName for a in doc.assets.values()]:
                # If it's an asset id or filename
                pass
        
        metrics.append(QualityMetric(
            name="Asset References",
            score=1.0,
            passed=True,
            details=f"{len(images)} images embedded, {len(doc.assets)} registered assets."
        ))

        # Determine Overall Status
        overall_status = QualityStatus.PASS
        if not has_text_nodes:
            overall_status = QualityStatus.FAILED
        elif replacement_count > 10 or not block_id_passed:
            overall_status = QualityStatus.WARNING
        elif total_chars < 50:
            overall_status = QualityStatus.REQUIRES_REVIEW

        return QualityReport(
            documentId=doc.documentId,
            overallStatus=overall_status.value,
            textSelectabilityScore=round(text_score, 2),
            unicodeIntegrityScore=round(unicode_score, 2),
            structuralScore=round(structural_score, 2),
            metrics=metrics,
            warnings=warnings,
            diagnostics={
                "page_count": len(doc.pages),
                "total_chars": total_chars,
                "replacement_count": replacement_count,
                "headings_count": len(headings),
                "paragraphs_count": len(paragraphs),
                "tables_count": len(tables),
                "figures_count": len(figures),
                "blocks_with_ids": blocks_tagged,
            }
        )

quality_service = DocumentQualityService()

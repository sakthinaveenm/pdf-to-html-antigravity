"""
Documents API Router.
Provides endpoints for document metadata, HTML retrieval, AST retrieval,
original PDF streaming, revision saves, asset streaming, and ZIP exports.
"""
import json
import uuid
import re
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

from backend.app.db.database import get_db
from backend.app.models.entities import Document, DocumentRevision
from backend.app.schemas.document import DocumentResponse, DocumentRevisionCreate, DocumentRevisionResponse
from backend.app.schemas.capabilities import QualityReport
from backend.app.config.settings import settings
from backend.app.services.html.normalizer import html_normalization_service
from backend.app.services.annotations.highlight_service import annotation_service
from backend.app.services.export.export_service import export_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_metadata(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    meta_dict = json.loads(doc.metadata_json) if doc.metadata_json else {}
    return DocumentResponse(
        id=doc.id,
        jobId=doc.job_id,
        title=doc.title,
        filename=doc.filename,
        sha256=doc.sha256,
        language=doc.language,
        pageCount=doc.page_count,
        currentRevision=doc.current_revision,
        qualityStatus=doc.quality_status,
        createdAt=doc.created_at,
        updatedAt=doc.updated_at,
        metadata=meta_dict
    )

@router.get("/{document_id}/html", response_class=HTMLResponse)
def get_document_html(document_id: str, db: Session = Depends(get_db)):
    doc_dir = settings.DOCUMENTS_DIR / document_id
    html_file = doc_dir / "document.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="HTML output not found for this document.")
    
    raw_html = html_file.read_text(encoding="utf-8")
    # Dynamically resolve relative asset paths (./assets/...) to API endpoints for web rendering
    resolved_html = re.sub(
        r'src=["\'](?:\./)?assets/([^"\']+)["\']',
        rf'src="/api/v1/documents/{document_id}/assets/\1"',
        raw_html
    )
    return HTMLResponse(content=resolved_html)

@router.get("/{document_id}/ast")
def get_document_ast(document_id: str):
    doc_dir = settings.DOCUMENTS_DIR / document_id
    ast_file = doc_dir / "document.json"
    if not ast_file.exists():
        raise HTTPException(status_code=404, detail="Canonical AST JSON not found for this document.")
    
    return json.loads(ast_file.read_text(encoding="utf-8"))

@router.get("/{document_id}/quality")
def get_document_quality(document_id: str):
    doc_dir = settings.DOCUMENTS_DIR / document_id
    q_file = doc_dir / "quality-report.json"
    if not q_file.exists():
        raise HTTPException(status_code=404, detail="Quality report not found.")
    
    return json.loads(q_file.read_text(encoding="utf-8"))

@router.get("/{document_id}/pdf")
def get_original_pdf(document_id: str):
    pdf_path = settings.ORIGINALS_DIR / f"{document_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Original PDF not found on disk.")
    
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{document_id}.pdf"
    )

@router.put("/{document_id}/revisions", response_model=DocumentRevisionResponse)
def save_revision(document_id: str, data: DocumentRevisionCreate, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc_dir = settings.DOCUMENTS_DIR / document_id
    revisions_dir = doc_dir / "revisions"
    revisions_dir.mkdir(parents=True, exist_ok=True)

    new_rev_num = doc.current_revision + 1
    doc.current_revision = new_rev_num

    # Normalize edited HTML
    normalized_html = html_normalization_service.normalize(data.html, document_id=document_id)

    # Save to storage
    (doc_dir / "document.html").write_text(normalized_html, encoding="utf-8")
    rev_file = revisions_dir / f"revision-{new_rev_num:03d}.html"
    rev_file.write_text(normalized_html, encoding="utf-8")

    # Extract block texts to execute re-anchoring of saved highlights
    soup = BeautifulSoup(normalized_html, "html.parser")
    block_texts = {}
    for elem in soup.find_all(lambda tag: tag.has_attr("data-block-id")):
        b_id = elem["data-block-id"]
        block_texts[b_id] = elem.get_text()

    annotation_service.reanchor_highlights_on_revision(db, document_id, new_rev_num, block_texts)

    # Re-build export ZIP with new HTML
    export_service.build_export_zip(document_id)

    rev_record = DocumentRevision(
        id=f"rev-{document_id}-{new_rev_num:03d}",
        document_id=document_id,
        revision_number=new_rev_num,
        html_content=normalized_html,
        change_summary=data.changeSummary
    )
    db.add(rev_record)
    db.commit()
    db.refresh(rev_record)

    return DocumentRevisionResponse(
        id=rev_record.id,
        documentId=rev_record.document_id,
        revisionNumber=rev_record.revision_number,
        changeSummary=rev_record.change_summary,
        createdAt=rev_record.created_at
    )

@router.get("/{document_id}/assets/{asset_filename}")
def get_document_asset(document_id: str, asset_filename: str):
    asset_path = settings.DOCUMENTS_DIR / document_id / "assets" / asset_filename
    if not asset_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found.")
    
    ext = asset_path.suffix.lower()
    mime = "image/png"
    if ext in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif ext == ".webp":
        mime = "image/webp"
    elif ext == ".svg":
        mime = "image/svg+xml"

    return FileResponse(path=asset_path, media_type=mime)

@router.get("/{document_id}/export")
def download_export_zip(document_id: str):
    zip_path = export_service.build_export_zip(document_id)
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{document_id}.zip"
    )


"""
Documents API Router.
Provides endpoints for document metadata, HTML retrieval, AST retrieval,
original PDF streaming, revision saves, asset streaming, and ZIP exports.
"""
import json
import uuid
import re
import shutil
import html
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from bs4 import BeautifulSoup

from backend.app.db.database import get_db
from backend.app.models.entities import Document, DocumentRevision, Highlight, Job
from backend.app.schemas.document import (
    DocumentResponse, DocumentRevisionCreate, DocumentRevisionResponse,
    DocumentListResponse, DocumentDeleteResponse, PageSnippetResponse,
    PageSnippetUpdateRequest
)
from backend.app.schemas.canonical import CanonicalDocument
from backend.app.schemas.capabilities import QualityReport
from backend.app.config.settings import settings
from backend.app.services.html.generator import html_generation_service
from backend.app.services.html.normalizer import html_normalization_service
from backend.app.services.annotations.highlight_service import annotation_service
from backend.app.services.export.export_service import export_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    total = query.count()
    records = query.order_by(desc(Document.created_at)).offset((page - 1) * limit).limit(limit).all()

    items = []
    for doc in records:
        meta_dict = json.loads(doc.metadata_json) if doc.metadata_json else {}
        items.append(DocumentResponse(
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
        ))

    return DocumentListResponse(total=total, items=items)

@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc_title = doc.title

    # 1. Delete associated jobs
    db.query(Job).filter(Job.document_id == document_id).delete(synchronize_session=False)

    # 2. Delete associated highlights and revisions
    db.query(Highlight).filter(Highlight.document_id == document_id).delete(synchronize_session=False)
    db.query(DocumentRevision).filter(DocumentRevision.document_id == document_id).delete(synchronize_session=False)

    # 3. Delete Document record
    db.delete(doc)
    db.commit()

    # 4. Clean up disk files
    doc_dir = settings.DOCUMENTS_DIR / document_id
    if doc_dir.exists():
        shutil.rmtree(doc_dir, ignore_errors=True)

    pdf_path = settings.ORIGINALS_DIR / f"{document_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink(missing_ok=True)

    return DocumentDeleteResponse(
        status="deleted",
        documentId=document_id,
        message=f"Document '{doc_title}' and all associated assets deleted successfully."
    )

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

# =========================================================================
# PAGE-BY-PAGE BOOK CONVERTER & EDITOR-READY HTML ENDPOINTS
# =========================================================================

@router.get("/{document_id}/pages/{page_number}/snippet", response_model=PageSnippetResponse)
def get_page_snippet(
    document_id: str,
    page_number: int,
    asset_base_url: Optional[str] = Query(None),
    embed_images: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get the EDITOR-READY HTML snippet for a specific PDF page.
    Includes inline CSS, preserved fonts/colors/alignments, and clean selectable DOM text.
    """
    doc_dir = settings.DOCUMENTS_DIR / document_id
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Document not found.")

    page_folder = doc_dir / "pages" / f"{page_number:04d}"
    paste_file = page_folder / "paste.html"

    # Auto-generate page bundle if not yet created on disk
    if not paste_file.exists():
        ast_file = doc_dir / "document.json"
        if not ast_file.exists():
            raise HTTPException(status_code=404, detail="Document AST not found.")
        doc_ast = CanonicalDocument.model_validate_json(ast_file.read_text(encoding="utf-8"))
        html_generation_service.generate_all_pages_bundle(doc_ast, doc_dir, asset_base_url=asset_base_url)

    # Dynamic generation if developer requests embedded Base64 images or custom CDN asset_base_url
    if embed_images or asset_base_url:
        ast_file = doc_dir / "document.json"
        if ast_file.exists():
            doc_ast = CanonicalDocument.model_validate_json(ast_file.read_text(encoding="utf-8"))
            html_snippet = html_generation_service.generate_page_snippet(
                doc_ast,
                page_number,
                asset_base_url=asset_base_url,
                embed_images_base64=embed_images,
                assets_dir=doc_dir / "assets"
            )
        else:
            html_snippet = paste_file.read_text(encoding="utf-8")
    else:
        html_snippet = paste_file.read_text(encoding="utf-8")
        # Ensure relative asset paths resolve to API endpoints for web previews
        html_snippet = re.sub(
            r'src=["\'](?:\./)?assets/([^"\']+)["\']',
            rf'src="/api/v1/documents/{document_id}/assets/\1"',
            html_snippet
        )

    soup = BeautifulSoup(html_snippet, "html.parser")
    plain_text = soup.get_text(separator="\n\n").strip()

    meta_file = page_folder / "metadata.json"
    meta_dict = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    is_corrected = (page_folder / "paste.original.html").exists()

    return PageSnippetResponse(
        documentId=document_id,
        pageNumber=page_number,
        html=html_snippet,
        plainText=plain_text,
        isCorrected=is_corrected,
        fontsDetected=meta_dict.get("fontsDetected", []),
        detectedScript=meta_dict.get("detectedScript"),
        wordCount=meta_dict.get("wordCount", len(plain_text.split())),
        warnings=[]
    )

@router.get("/{document_id}/pages/{page_number}/standalone", response_class=HTMLResponse)
def get_page_standalone(document_id: str, page_number: int):
    """
    Get full STANDALONE HTML document for previewing or downloading a single page.
    """
    doc_dir = settings.DOCUMENTS_DIR / document_id
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Document not found.")

    page_folder = doc_dir / "pages" / f"{page_number:04d}"
    standalone_file = page_folder / "standalone.html"

    if not standalone_file.exists():
        ast_file = doc_dir / "document.json"
        if not ast_file.exists():
            raise HTTPException(status_code=404, detail="Document AST not found.")
        doc_ast = CanonicalDocument.model_validate_json(ast_file.read_text(encoding="utf-8"))
        html_generation_service.generate_all_pages_bundle(doc_ast, doc_dir)

    raw_html = standalone_file.read_text(encoding="utf-8")
    resolved_html = re.sub(
        r'src=["\'](?:\./)?assets/([^"\']+)["\']',
        rf'src="/api/v1/documents/{document_id}/assets/\1"',
        raw_html
    )
    return HTMLResponse(content=resolved_html)

@router.put("/{document_id}/pages/{page_number}/snippet", response_model=PageSnippetResponse)
def update_page_snippet(
    document_id: str,
    page_number: int,
    data: PageSnippetUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Save manual developer corrections to a specific page's HTML locally without modifying the source PDF.
    Preserves original snippet in paste.original.html for easy reset.
    """
    doc_dir = settings.DOCUMENTS_DIR / document_id
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Document not found.")

    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    page_folder = doc_dir / "pages" / f"{page_number:04d}"
    page_folder.mkdir(parents=True, exist_ok=True)
    paste_file = page_folder / "paste.html"
    backup_file = page_folder / "paste.original.html"

    # Backup original snippet before first manual edit
    if paste_file.exists() and not backup_file.exists():
        shutil.copy2(paste_file, backup_file)

    # Save edited snippet
    paste_file.write_text(data.html, encoding="utf-8")

    # Update standalone single page preview
    standalone_file = page_folder / "standalone.html"
    title = f"{doc.title} - Page {page_number}"
    reader_css = html_generation_service.get_reader_css()
    standalone_html = f"""<!DOCTYPE html>
<html lang="{doc.language}" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <style>
{reader_css}
  </style>
</head>
<body>
  <div class="document-container">
{data.html}
  </div>
</body>
</html>"""
    standalone_file.write_text(standalone_html, encoding="utf-8")

    # Re-synthesize full document.html
    pages_root = doc_dir / "pages"
    all_snippets = []
    for p_dir in sorted(pages_root.glob("*")):
        if p_dir.is_dir():
            pf = p_dir / "paste.html"
            if pf.exists():
                all_snippets.append(pf.read_text(encoding="utf-8"))

    if all_snippets:
        combined_inner = "\n".join(all_snippets)
        combined_doc = f"""<!DOCTYPE html>
<html lang="{doc.language}" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(doc.title)}</title>
  <style>
{reader_css}
  </style>
</head>
<body>
  <div class="document-container">
<article class="canonical-document" lang="{doc.language}" data-document-id="{document_id}">
{combined_inner}
</article>
  </div>
</body>
</html>"""
        (doc_dir / "document.html").write_text(combined_doc, encoding="utf-8")

    # Bump revision
    doc.current_revision += 1
    db.commit()

    # Re-build export ZIP
    export_service.build_export_zip(document_id)

    soup = BeautifulSoup(data.html, "html.parser")
    plain_text = soup.get_text(separator="\n\n").strip()

    meta_file = page_folder / "metadata.json"
    meta_dict = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}

    return PageSnippetResponse(
        documentId=document_id,
        pageNumber=page_number,
        html=data.html,
        plainText=plain_text,
        isCorrected=True,
        fontsDetected=meta_dict.get("fontsDetected", []),
        detectedScript=meta_dict.get("detectedScript"),
        wordCount=meta_dict.get("wordCount", len(plain_text.split())),
        warnings=[]
    )

@router.post("/{document_id}/pages/{page_number}/reset", response_model=PageSnippetResponse)
def reset_page_snippet(document_id: str, page_number: int, db: Session = Depends(get_db)):
    """
    Reset a manually corrected page back to its original converted HTML snippet.
    """
    doc_dir = settings.DOCUMENTS_DIR / document_id
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Document not found.")

    page_folder = doc_dir / "pages" / f"{page_number:04d}"
    paste_file = page_folder / "paste.html"
    backup_file = page_folder / "paste.original.html"

    if backup_file.exists():
        shutil.copy2(backup_file, paste_file)
        backup_file.unlink()
    else:
        # Regenerate from AST
        ast_file = doc_dir / "document.json"
        if ast_file.exists():
            doc_ast = CanonicalDocument.model_validate_json(ast_file.read_text(encoding="utf-8"))
            snippet = html_generation_service.generate_page_snippet(doc_ast, page_number, assets_dir=doc_dir / "assets")
            paste_file.write_text(snippet, encoding="utf-8")

    # Re-synthesize full document.html
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        pages_root = doc_dir / "pages"
        all_snippets = []
        for p_dir in sorted(pages_root.glob("*")):
            if p_dir.is_dir():
                pf = p_dir / "paste.html"
                if pf.exists():
                    all_snippets.append(pf.read_text(encoding="utf-8"))

        if all_snippets:
            reader_css = html_generation_service.get_reader_css()
            combined_inner = "\n".join(all_snippets)
            combined_doc = f"""<!DOCTYPE html>
<html lang="{doc.language}" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(doc.title)}</title>
  <style>
{reader_css}
  </style>
</head>
<body>
  <div class="document-container">
<article class="canonical-document" lang="{doc.language}" data-document-id="{document_id}">
{combined_inner}
</article>
  </div>
</body>
</html>"""
            (doc_dir / "document.html").write_text(combined_doc, encoding="utf-8")

    export_service.build_export_zip(document_id)
    return get_page_snippet(document_id, page_number, db=db)

@router.get("/{document_id}/pages/{page_number}/export")
def download_page_export(document_id: str, page_number: int, format: str = Query("paste")):
    """
    Download a single page's HTML file (either editor-ready paste fragment or standalone HTML).
    """
    doc_dir = settings.DOCUMENTS_DIR / document_id
    page_folder = doc_dir / "pages" / f"{page_number:04d}"
    if not page_folder.exists():
        raise HTTPException(status_code=404, detail="Page not found.")

    target_file = page_folder / "standalone.html" if format == "standalone" else page_folder / "paste.html"
    if not target_file.exists():
        raise HTTPException(status_code=404, detail="Export file not found.")

    return FileResponse(
        path=target_file,
        media_type="text/html",
        filename=f"page-{page_number:04d}-{format}.html"
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


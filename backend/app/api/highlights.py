"""
Highlights API Router.
CRUD endpoints for persistent text annotations with quote and position anchoring.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.entities import Document
from backend.app.schemas.highlight import HighlightCreate, HighlightUpdate, HighlightResponse, TextQuote, TextPosition
from backend.app.services.annotations.highlight_service import annotation_service

router = APIRouter(prefix="/documents/{document_id}/highlights", tags=["Highlights"])

@router.post("", response_model=HighlightResponse)
def create_highlight(document_id: str, data: HighlightCreate, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    highlight = annotation_service.create_highlight(
        db=db,
        document_id=document_id,
        data=data,
        revision=doc.current_revision
    )

    import json
    return HighlightResponse(
        id=highlight.id,
        documentId=highlight.document_id,
        revision=highlight.revision,
        blockIds=json.loads(highlight.block_ids) if highlight.block_ids else [],
        quote=TextQuote(exact=highlight.exact_text, prefix=highlight.prefix, suffix=highlight.suffix),
        position=TextPosition(start=highlight.start_offset, end=highlight.end_offset, unit=highlight.offset_unit),
        color=highlight.color,
        note=highlight.note,
        resolved=highlight.resolved,
        createdAt=highlight.created_at,
        updatedAt=highlight.updated_at
    )

@router.get("", response_model=List[HighlightResponse])
def get_highlights(document_id: str, db: Session = Depends(get_db)):
    return annotation_service.list_highlights(db, document_id)

@router.patch("/{highlight_id}", response_model=HighlightResponse)
def update_highlight(document_id: str, highlight_id: str, data: HighlightUpdate, db: Session = Depends(get_db)):
    res = annotation_service.update_highlight(db, highlight_id, data)
    if not res:
        raise HTTPException(status_code=404, detail="Highlight not found.")
    return res

@router.delete("/{highlight_id}")
def delete_highlight(document_id: str, highlight_id: str, db: Session = Depends(get_db)):
    deleted = annotation_service.delete_highlight(db, highlight_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Highlight not found.")
    return {"status": "success", "message": "Highlight deleted."}


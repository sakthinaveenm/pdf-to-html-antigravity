"""
Durable Text Selection and Highlighting Service.
Handles Text Quote Anchoring, Unicode Codepoints vs UTF-16 code units,
fuzzy re-anchoring on document revisions, and highlight persistence.
"""
from typing import List, Dict, Any, Optional, Tuple
import json
import uuid
from sqlalchemy.orm import Session
from backend.app.models.entities import Highlight, Document
from backend.app.schemas.highlight import HighlightCreate, HighlightUpdate, HighlightResponse, TextQuote, TextPosition

def utf16_offset_to_codepoint_offset(text: str, utf16_offset: int) -> int:
    """
    Convert a UTF-16 code unit offset (used by JS DOM Range)
    to a Unicode codepoint offset.
    Handles surrogate pairs (SMP characters > U+FFFF, e.g. emojis or rare CJK).
    """
    codepoints = 0
    current_utf16 = 0
    for char in text:
        if current_utf16 >= utf16_offset:
            break
        # If character is in Supplementary Plane (ord > 0xFFFF), it occupies 2 UTF-16 code units
        code_units = 2 if ord(char) > 0xFFFF else 1
        current_utf16 += code_units
        codepoints += 1
    return codepoints

def codepoint_offset_to_utf16_offset(text: str, codepoint_offset: int) -> int:
    """
    Convert a Unicode codepoint offset to a UTF-16 code unit offset
    for JS DOM Range application.
    """
    utf16_offset = 0
    for i, char in enumerate(text):
        if i >= codepoint_offset:
            break
        utf16_offset += 2 if ord(char) > 0xFFFF else 1
    return utf16_offset

class AnnotationService:
    @staticmethod
    def create_highlight(db: Session, document_id: str, data: HighlightCreate, revision: int = 1) -> Highlight:
        highlight_id = f"hl-{uuid.uuid4().hex[:10]}"
        record = Highlight(
            id=highlight_id,
            document_id=document_id,
            revision=revision,
            block_ids=json.dumps(data.blockIds),
            exact_text=data.quote.exact,
            prefix=data.quote.prefix,
            suffix=data.quote.suffix,
            start_offset=data.position.start,
            end_offset=data.position.end,
            offset_unit=data.position.unit,
            color=data.color,
            note=data.note,
            resolved=True
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def list_highlights(db: Session, document_id: str) -> List[HighlightResponse]:
        records = db.query(Highlight).filter(Highlight.document_id == document_id).all()
        results: List[HighlightResponse] = []
        for r in records:
            results.append(HighlightResponse(
                id=r.id,
                documentId=r.document_id,
                revision=r.revision,
                blockIds=json.loads(r.block_ids) if r.block_ids else [],
                quote=TextQuote(exact=r.exact_text, prefix=r.prefix, suffix=r.suffix),
                position=TextPosition(start=r.start_offset, end=r.end_offset, unit=r.offset_unit),
                color=r.color,
                note=r.note,
                resolved=r.resolved,
                createdAt=r.created_at,
                updatedAt=r.updated_at
            ))
        return results

    @staticmethod
    def update_highlight(db: Session, highlight_id: str, data: HighlightUpdate) -> Optional[HighlightResponse]:
        record = db.query(Highlight).filter(Highlight.id == highlight_id).first()
        if not record:
            return None
        if data.color is not None:
            record.color = data.color
        if data.note is not None:
            record.note = data.note
        if data.resolved is not None:
            record.resolved = data.resolved
        db.commit()
        db.refresh(record)
        return HighlightResponse(
            id=record.id,
            documentId=record.document_id,
            revision=record.revision,
            blockIds=json.loads(record.block_ids) if record.block_ids else [],
            quote=TextQuote(exact=record.exact_text, prefix=record.prefix, suffix=record.suffix),
            position=TextPosition(start=record.start_offset, end=record.end_offset, unit=record.offset_unit),
            color=record.color,
            note=record.note,
            resolved=record.resolved,
            createdAt=record.created_at,
            updatedAt=record.updated_at
        )

    @staticmethod
    def delete_highlight(db: Session, highlight_id: str) -> bool:
        record = db.query(Highlight).filter(Highlight.id == highlight_id).first()
        if not record:
            return False
        db.delete(record)
        db.commit()
        return True

    @staticmethod
    def reanchor_highlights_on_revision(db: Session, document_id: str, new_revision: int, block_texts: Dict[str, str]):
        """
        Re-anchoring algorithm:
        Checks each saved highlight against the new content of target block(s).
        Uses Text Quote Anchoring (exact + prefix + suffix) to relocate offsets,
        or marks the highlight as resolved=False if text no longer exists.
        """
        highlights = db.query(Highlight).filter(Highlight.document_id == document_id).all()
        for h in highlights:
            block_ids = json.loads(h.block_ids) if h.block_ids else []
            if not block_ids or block_ids[0] not in block_texts:
                h.resolved = False
                continue

            target_text = block_texts[block_ids[0]]
            exact = h.exact_text

            # 1. Exact match check
            if exact in target_text:
                # If multiple occurrences, disambiguate using prefix/suffix
                idx = -1
                full_pattern = f"{h.prefix}{exact}{h.suffix}"
                if full_pattern in target_text:
                    idx = target_text.find(full_pattern) + len(h.prefix)
                else:
                    idx = target_text.find(exact)

                if idx >= 0:
                    h.start_offset = idx
                    h.end_offset = idx + len(exact)
                    h.revision = new_revision
                    h.resolved = True
                    continue

            # Could not re-anchor safely
            h.resolved = False
            h.revision = new_revision

        db.commit()

annotation_service = AnnotationService()


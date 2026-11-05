"""
Jobs API Router.
Supports batch PDF uploads, pagination, progress polling, cancellation, and retries.
"""
import uuid
import hashlib
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.database import get_db
from backend.app.models.entities import Job
from backend.app.schemas.job import JobResponse, JobListResponse, BatchUploadResponse
from backend.app.config.settings import settings
from backend.app.constants.statuses import JobStatus

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=BatchUploadResponse)
async def create_jobs(
    files: List[UploadFile] = File(...),
    converter: str = Form("AUTO"),
    ocr_languages: str = Form("eng+tam+hin"),
    force_ocr: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Batch upload multiple PDF files and queue them for conversion.
    Each file receives an independent job ID and document ID.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    created_jobs: List[JobResponse] = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue

        content = await file.read()
        file_size = len(content)
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} exceeds maximum size limit ({settings.MAX_UPLOAD_SIZE_BYTES / (1024*1024):.0f}MB)."
            )

        sha256_hash = hashlib.sha256(content).hexdigest()
        job_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())

        # Save to storage/originals/{doc_id}.pdf
        target_path = settings.ORIGINALS_DIR / f"{doc_id}.pdf"
        target_path.write_bytes(content)

        job_record = Job(
            id=job_id,
            document_id=doc_id,
            filename=file.filename,
            file_path=str(target_path),
            file_size=file_size,
            sha256=sha256_hash,
            status=JobStatus.QUEUED.value,
            converter=converter.upper(),
            ocr_languages=ocr_languages,
            force_ocr=force_ocr,
            progress=0,
            current_step="Queued"
        )
        db.add(job_record)
        db.commit()
        db.refresh(job_record)

        created_jobs.append(JobResponse(
            id=job_record.id,
            documentId=job_record.document_id,
            filename=job_record.filename,
            fileSize=job_record.file_size,
            sha256=job_record.sha256,
            status=job_record.status,
            converter=job_record.converter,
            ocrLanguages=job_record.ocr_languages,
            forceOcr=job_record.force_ocr,
            progress=job_record.progress,
            currentStep=job_record.current_step,
            errorMessage=job_record.error_message,
            createdAt=job_record.created_at,
            updatedAt=job_record.updated_at,
            completedAt=job_record.completed_at
        ))

    return BatchUploadResponse(jobs=created_jobs)

@router.get("", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status.upper())
    
    total = query.count()
    records = query.order_by(desc(Job.created_at)).offset((page - 1) * limit).limit(limit).all()

    items = [
        JobResponse(
            id=r.id,
            documentId=r.document_id,
            filename=r.filename,
            fileSize=r.file_size,
            sha256=r.sha256,
            status=r.status,
            converter=r.converter,
            ocrLanguages=r.ocr_languages,
            forceOcr=r.force_ocr,
            progress=r.progress,
            currentStep=r.current_step,
            errorMessage=r.error_message,
            createdAt=r.created_at,
            updatedAt=r.updated_at,
            completedAt=r.completed_at
        )
        for r in records
    ]

    return JobListResponse(total=total, items=items)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    record = db.query(Job).filter(Job.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    return JobResponse(
        id=record.id,
        documentId=record.document_id,
        filename=record.filename,
        fileSize=record.file_size,
        sha256=record.sha256,
        status=record.status,
        converter=record.converter,
        ocrLanguages=record.ocr_languages,
        forceOcr=record.force_ocr,
        progress=record.progress,
        currentStep=record.current_step,
        errorMessage=record.error_message,
        createdAt=record.created_at,
        updatedAt=record.updated_at,
        completedAt=record.completed_at
    )

@router.post("/{job_id}/cancel")
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    record = db.query(Job).filter(Job.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    if record.status in (JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELED.value):
        return {"status": record.status, "message": "Job is already terminated."}

    record.status = JobStatus.CANCELED.value
    record.current_step = "Canceled by user"
    db.commit()
    return {"status": JobStatus.CANCELED.value, "message": "Job successfully canceled."}

@router.post("/{job_id}/retry")
def retry_job(job_id: str, db: Session = Depends(get_db)):
    record = db.query(Job).filter(Job.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    record.status = JobStatus.QUEUED.value
    record.progress = 0
    record.current_step = "Queued for retry"
    record.error_message = None
    db.commit()
    return {"status": JobStatus.QUEUED.value, "message": "Job queued for retry."}


"""
Integration tests for FastAPI REST APIs.
"""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.entities import Job
from backend.app.workers.job_worker import job_processor

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_capabilities_endpoint(client):
    res = client.get("/api/v1/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert "platform" in data
    assert len(data["installedOcrLanguages"]) > 0
    assert len(data["converters"]) > 0

def test_batch_upload_and_pipeline(client):
    pdf_path = Path("samples/sample_english.pdf")
    with open(pdf_path, "rb") as f:
        res = client.post(
            "/api/v1/jobs",
            files={"files": ("sample_english.pdf", f, "application/pdf")},
            data={"converter": "NATIVE", "ocr_languages": "eng"}
        )
    assert res.status_code == 200
    data = res.json()
    assert "jobs" in data
    assert len(data["jobs"]) == 1
    job_info = data["jobs"][0]
    job_id = job_info["id"]
    doc_id = job_info["documentId"]

    # Process job synchronously
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    job_processor._process_single_job(db, job)
    db.close()

    # Verify Job is COMPLETED
    job_res = client.get(f"/api/v1/jobs/{job_id}")
    assert job_res.status_code == 200
    assert job_res.json()["status"] == "COMPLETED"

    # Verify Document Metadata
    doc_res = client.get(f"/api/v1/documents/{doc_id}")
    assert doc_res.status_code == 200
    assert doc_res.json()["id"] == doc_id

    # Verify Generated HTML
    html_res = client.get(f"/api/v1/documents/{doc_id}/html")
    assert html_res.status_code == 200
    assert "Multilingual Document Processing Architecture" in html_res.text
    assert "<article" in html_res.text

    # Verify Canonical AST
    ast_res = client.get(f"/api/v1/documents/{doc_id}/ast")
    assert ast_res.status_code == 200
    ast_data = ast_res.json()
    assert ast_data["documentId"] == doc_id
    assert len(ast_data["blocks"]) > 0

    # Verify Quality Report
    qual_res = client.get(f"/api/v1/documents/{doc_id}/quality")
    assert qual_res.status_code == 200
    assert qual_res.json()["textSelectabilityScore"] > 0

    # Test Revision saving
    rev_res = client.put(
        f"/api/v1/documents/{doc_id}/revisions",
        json={"html": html_res.text, "changeSummary": "Editor test revision"}
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["revisionNumber"] == 2

    # Test Highlight Creation
    hl_res = client.post(
        f"/api/v1/documents/{doc_id}/highlights",
        json={
            "blockIds": [ast_data["blocks"][0]["blockId"]],
            "quote": {"exact": "Multilingual", "prefix": "", "suffix": " Document"},
            "position": {"start": 0, "end": 12, "unit": "unicode-codepoint"},
            "color": "#FFEB3B"
        }
    )
    assert hl_res.status_code == 200
    hl_id = hl_res.json()["id"]

    # Test List Highlights
    list_hl = client.get(f"/api/v1/documents/{doc_id}/highlights")
    assert list_hl.status_code == 200
    assert len(list_hl.json()) == 1

    # Test Export ZIP Download
    export_res = client.get(f"/api/v1/documents/{doc_id}/export")
    assert export_res.status_code == 200
    assert export_res.headers["content-type"] == "application/zip"
    assert len(export_res.content) > 100


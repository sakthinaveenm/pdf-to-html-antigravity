# REST API Reference Manual

Base URL: `http://localhost:8000/api/v1`

---

## 1. System & Health

### `GET /health`
Returns system health status.
**Response (200 OK)**:
```json
{
  "status": "healthy",
  "app": "Multilingual PDF to HTML Converter",
  "version": "1.0.0"
}
```

### `GET /capabilities`
Returns host system hardware profile, installed Tesseract OCR languages, and document converter availability.
**Response (200 OK)**:
```json
{
  "platform": "macOS-27.2-arm64-arm-64bit",
  "cpuCount": 10,
  "totalRamGb": 16.0,
  "gpuAvailable": true,
  "gpuName": "Apple Metal Performance Shaders (MPS)",
  "gpuMemoryMb": 11468,
  "recommendedDevice": "mps",
  "defaultWorkers": 1,
  "installedOcrLanguages": ["eng", "tam", "hin", "ara", "chi_sim", "..."],
  "converters": [
    { "name": "NATIVE", "available": true, "version": "2.1", "description": "PyMuPDF + Tesseract" },
    { "name": "DOCLING", "available": true, "version": "2.147.0", "description": "IBM Docling" },
    { "name": "MARKER", "available": true, "version": "2.1.0", "description": "Marker Surya Layout" }
  ],
  "defaultConverter": "AUTO"
}
```

---

## 2. Jobs Queue

### `POST /jobs`
Batch upload multiple PDF files and queue them for conversion.
**Content-Type**: `multipart/form-data`
**Parameters**:
- `files`: Array of `.pdf` binary files (up to 150MB each)
- `converter`: `AUTO` | `MARKER` | `DOCLING` | `NATIVE` (default: `AUTO`)
- `ocr_languages`: Language codes combined with `+` (e.g. `eng+tam+hin`)
- `force_ocr`: Boolean (default: `false`)

**Response (200 OK)**:
```json
{
  "jobs": [
    {
      "id": "e8d67280-928d-4f10-91aa-9f056d649ab1",
      "documentId": "4c9470d0-fb16-46b0-96f7-4638a143f550",
      "filename": "sample_tamil.pdf",
      "fileSize": 245100,
      "sha256": "7a3f89e2...",
      "status": "QUEUED",
      "converter": "AUTO",
      "ocrLanguages": "eng+tam+hin",
      "forceOcr": false,
      "progress": 0,
      "currentStep": "Queued",
      "createdAt": "2026-11-05T19:00:00Z",
      "updatedAt": "2026-11-05T19:00:00Z"
    }
  ]
}
```

### `GET /jobs`
List conversion jobs with pagination and status filtering.
**Query Parameters**:
- `page`: Integer (default: 1)
- `limit`: Integer (default: 20, max: 100)
- `status`: Optional filter (`QUEUED`, `INSPECTING`, `CONVERTING`, `COMPLETED`, `FAILED`, `CANCELED`)

### `GET /jobs/{jobId}`
Fetch real-time progress (0–100%) and current execution step.

### `POST /jobs/{jobId}/cancel`
Cancel an active or queued conversion job.

### `POST /jobs/{jobId}/retry`
Re-queue a failed or canceled job.

---

## 3. Documents & Content

### `GET /documents/{documentId}`
Fetch document metadata, page count, language, and quality status.

### `GET /documents/{documentId}/html`
Returns the generated semantic HTML document (`text/html; charset=utf-8`).

### `GET /documents/{documentId}/ast`
Returns the versioned Canonical Document Model AST in JSON format.

### `GET /documents/{documentId}/pdf`
Stream the original source PDF for side-by-side comparison.

### `GET /documents/{documentId}/quality`
Returns the quality verification report with selectability scores, Unicode integrity, and structural diagnostics.

### `PUT /documents/{documentId}/revisions`
Save an updated HTML revision (from TipTap or manual editor). Triggers automatic re-anchoring of saved highlights.
**Request Body**:
```json
{
  "html": "<article ...>...</article>",
  "changeSummary": "Corrected heading typo"
}
```

### `GET /documents/{documentId}/assets/{assetFilename}`
Serve extracted raster images with appropriate caching and mime-types.

### `GET /documents/{documentId}/export`
Download the self-contained offline ZIP bundle.

---

## 4. Annotations & Highlights

### `POST /documents/{documentId}/highlights`
Create a durable text highlight.
**Request Body**:
```json
{
  "blockIds": ["blk-p1-s002-c3d4"],
  "quote": {
    "exact": "தமிழ் ஒரு அழகான மொழி",
    "prefix": "",
    "suffix": "."
  },
  "position": {
    "start": 0,
    "end": 22,
    "unit": "unicode-codepoint"
  },
  "color": "#FFEB3B",
  "note": "Optional annotation note"
}
```

### `GET /documents/{documentId}/highlights`
List all saved highlights for the document.

### `PATCH /documents/{documentId}/highlights/{highlightId}`
Update highlight color or note.

### `DELETE /documents/{documentId}/highlights/{highlightId}`
Delete a highlight by ID.

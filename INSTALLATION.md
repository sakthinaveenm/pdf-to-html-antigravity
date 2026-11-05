# Installation & Setup Guide

This guide provides step-by-step installation instructions for macOS, Linux, and Windows for the Multilingual PDF to HTML Conversion Platform.

---

## 1. Prerequisites

- **Python**: Version 3.11+
- **Node.js**: Version 18+ (Node 20+ or 24 recommended)
- **Tesseract OCR**: Version 5.x with multilingual language packs
- **Poppler / pdftoppm**: Required for raster PDF rendering and page geometry inspection

---

## 2. OS-Specific System Dependencies

### macOS (Apple Silicon & Intel)
Using Homebrew:
```bash
# Install Poppler and Tesseract
brew install poppler tesseract

# Install all language packs or target multilingual packs
brew install tesseract-lang
```
Verify installation:
```bash
tesseract --version
tesseract --list-langs | grep -E "tam|hin|ara|urd|chi_sim|jpn|kor"
```

### Linux (Ubuntu / Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-all \
    libgl1-mesa-glx \
    libglib2.0-0
```

### Windows (PowerShell)
1. Install Python 3.11 from python.org (ensure "Add Python to PATH" is checked).
2. Install Tesseract using UB-Mannheim installer:
   - Download installer: `https://github.com/UB-Mannheim/tesseract/wiki`
   - During setup, select "Additional language data" and check Tamil, Hindi, Arabic, CJK, etc.
   - Add `C:\Program Files\Tesseract-OCR` to system PATH.
3. Install Poppler for Windows and add `bin` to PATH.

---

## 3. Backend Setup

```bash
# 1. Clone repository and enter project root
cd /path/to/pdf-to-html-antigravity

# 2. Create Python 3.11 virtual environment
python3.11 -m venv .venv

# 3. Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

# 4. Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# 5. Install pinned backend dependencies
pip install -r backend/requirements.txt
```

---

## 4. Frontend Setup

```bash
# Enter frontend directory
cd frontend

# Install Node dependencies
npm install

# Build production bundle
npm run build
```

---

## 5. Running the Application Locally

### Running Backend (Terminal 1)
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`
- Capabilities: `http://localhost:8000/api/v1/capabilities`

### Running Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Web Application will be available at:
- Web App UI: `http://localhost:5173`

---

## 6. Docker Deployment (Optional)

```bash
docker compose -f docker/docker-compose.yml up --build
```
- Web Application: `http://localhost:3000`
- REST API: `http://localhost:8000`


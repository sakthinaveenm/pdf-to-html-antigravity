#!/usr/bin/env bash
# ==============================================================================
# Multilingual PDF to HTML Platform - Launch Script (macOS / Linux)
# Unique Ports:
#   - Backend API: 8844
#   - Frontend UI: 5188
# ==============================================================================

set -e

BACKEND_PORT="${BACKEND_PORT:-8844}"
FRONTEND_PORT="${FRONTEND_PORT:-5188}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================================="
echo "🌐 Starting Multilingual PDF to HTML Platform Setup & Launch"
echo "   Backend Port:  $BACKEND_PORT (Unique)"
echo "   Frontend Port: $FRONTEND_PORT (Unique)"
echo "=========================================================================="

# ------------------------------------------------------------------------------
# 1. Check Python 3.11+
# ------------------------------------------------------------------------------
PY_CMD=""
CANDIDATES=(
    "$ROOT_DIR/.venv/bin/python"
    "python3.11"
    "python3.12"
    "python3.13"
    "$HOME/.local/bin/python3.11"
    "/opt/homebrew/bin/python3.11"
    "/usr/local/bin/python3.11"
    "python3"
    "python"
)

for cand in "${CANDIDATES[@]}"; do
    if command -v "$cand" &>/dev/null || [ -f "$cand" ]; then
        if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' &>/dev/null; then
            PY_CMD="$cand"
            break
        fi
    fi
done

if [ -z "$PY_CMD" ]; then
    echo "❌ Error: Python 3.11 or higher is required but was not found on your system."
    echo "   Please install Python 3.11+: https://www.python.org/downloads/"
    exit 1
fi

PY_VER=$($PY_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PY_VER found ($PY_CMD)."

# ------------------------------------------------------------------------------
# 2. Check Node.js & npm
# ------------------------------------------------------------------------------
if ! command -v node &>/dev/null; then
    echo "❌ Error: Node.js is not installed."
    echo "   Please install Node.js 18+: https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js $(node --version) found."

if ! command -v npm &>/dev/null; then
    echo "❌ Error: npm is not installed."
    exit 1
fi
echo "✅ npm $(npm --version) found."

# ------------------------------------------------------------------------------
# 3. Check System Tools (Tesseract & Poppler)
# ------------------------------------------------------------------------------
if command -v tesseract &>/dev/null; then
    echo "✅ Tesseract OCR found: $(tesseract --version 2>&1 | head -n 1)"
else
    echo "⚠️  Notice: Tesseract OCR is not installed or not in PATH."
    echo "   Scanned document OCR will use CPU fallback or report un-OCRed images."
    echo "   Install on macOS: brew install tesseract tesseract-lang"
    echo "   Install on Linux: sudo apt-get install tesseract-ocr tesseract-ocr-all"
fi

if command -v pdftoppm &>/dev/null; then
    echo "✅ Poppler (pdftoppm) found."
else
    echo "⚠️  Notice: Poppler (pdftoppm) is not found."
    echo "   Install on macOS: brew install poppler"
    echo "   Install on Linux: sudo apt-get install poppler-utils"
fi

# ------------------------------------------------------------------------------
# 4. Check & Prepare Python Virtual Environment
# ------------------------------------------------------------------------------
VENV_DIR="$ROOT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating Python virtual environment at .venv..."
    $PY_CMD -m venv "$VENV_DIR"
fi

# Activate virtualenv
source "$VENV_DIR/bin/activate"

# ------------------------------------------------------------------------------
# 5. Check & Install Backend Dependencies
# ------------------------------------------------------------------------------
echo "🔍 Checking Python backend dependencies..."
NEED_PIP_INSTALL=false
if ! python -c "import fastapi, uvicorn, pydantic, sqlalchemy, pymupdf, nh3" &>/dev/null; then
    NEED_PIP_INSTALL=true
fi

if [ "$NEED_PIP_INSTALL" = true ]; then
    echo "📦 Installing backend packages from backend/requirements.txt..."
    if command -v uv &>/dev/null; then
        echo "   (Using uv for fast package installation)"
        uv pip install -r "$ROOT_DIR/backend/requirements.txt"
    else
        pip install --upgrade pip setuptools wheel
        pip install -r "$ROOT_DIR/backend/requirements.txt"
    fi
    echo "✅ Backend dependencies installed."
else
    echo "✅ Backend dependencies are already verified."
fi

# ------------------------------------------------------------------------------
# 6. Check & Install Frontend Dependencies
# ------------------------------------------------------------------------------
echo "🔍 Checking frontend dependencies..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ] || [ ! -d "node_modules/vite" ]; then
    echo "📦 Installing frontend npm dependencies..."
    npm install
    echo "✅ Frontend dependencies installed."
else
    echo "✅ Frontend dependencies are already verified."
fi
cd "$ROOT_DIR"

# ------------------------------------------------------------------------------
# 7. Check Port Availability & Free If Stale
# ------------------------------------------------------------------------------
free_port() {
    local port=$1
    if command -v lsof &>/dev/null; then
        local pid
        pid=$(lsof -ti :"$port" || true)
        if [ -n "$pid" ]; then
            echo "⚠️  Port $port in use by PID $pid. Terminating stale process..."
            kill -9 "$pid" 2>/dev/null || true
            sleep 1
        fi
    fi
}

free_port "$BACKEND_PORT"
free_port "$FRONTEND_PORT"

# ------------------------------------------------------------------------------
# 8. Launch Backend & Frontend with Clean Process Management
# ------------------------------------------------------------------------------
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo "👋 Shutdown complete."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo ""
echo "🚀 Starting FastAPI Backend on port $BACKEND_PORT..."
export PYTHONPATH="$ROOT_DIR"
uvicorn backend.app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!

# Wait 2 seconds for backend to start up
sleep 2

echo "🚀 Starting React Frontend on port $FRONTEND_PORT..."
cd "$ROOT_DIR/frontend"
export BACKEND_PORT="$BACKEND_PORT"
export VITE_BACKEND_PORT="$BACKEND_PORT"
export PORT="$FRONTEND_PORT"
npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$ROOT_DIR"

echo ""
echo "=========================================================================="
echo "🎉 MULTILINGUAL PDF TO HTML PLATFORM IS RUNNING!"
echo "=========================================================================="
echo "  📱 Web Application:   http://localhost:$FRONTEND_PORT"
echo "  ⚙️  REST API Docs:     http://localhost:$BACKEND_PORT/docs"
echo "  🩺 Health Endpoint:   http://localhost:$BACKEND_PORT/api/v1/health"
echo "  ⚡ Unique Ports:       Backend $BACKEND_PORT | Frontend $FRONTEND_PORT"
echo "=========================================================================="
echo "Press Ctrl+C to stop both servers."
echo ""

# Keep running until Ctrl+C
wait

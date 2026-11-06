@echo off
setlocal enabledelayedexpansion

:: ==============================================================================
:: Multilingual PDF to HTML Platform - Launch Script (Windows CMD)
:: Unique Ports:
::   - Backend API: 8844
::   - Frontend UI: 5188
:: ==============================================================================

title Multilingual PDF to HTML Converter Launcher

if "%BACKEND_PORT%"=="" set BACKEND_PORT=8844
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=5188
set ROOT_DIR=%~dp0

echo ==========================================================================
echo   Starting Multilingual PDF to HTML Platform Setup ^& Launch (Windows)
echo   Backend Port:  %BACKEND_PORT% (Unique)
echo   Frontend Port: %FRONTEND_PORT% (Unique)
echo ==========================================================================

:: 1. Search for Python 3.11+
set PY_CMD=
if exist "%ROOT_DIR%.venv\Scripts\python.exe" (
    "%ROOT_DIR%.venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 set PY_CMD="%ROOT_DIR%.venv\Scripts\python.exe"
)

if "%PY_CMD%"=="" (
    py -3.11 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 set PY_CMD=py -3.11
)

if "%PY_CMD%"=="" (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 set PY_CMD=python
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python 3.11 or higher is not found on PATH.
    echo Please install Python 3.11+: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python verified using %PY_CMD%.

:: 2. Check Node.js and npm
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not found on PATH.
    echo Please install Node.js (18+): https://nodejs.org/
    pause
    exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed or not found on PATH.
    pause
    exit /b 1
)
echo [OK] Node.js and npm verified.

:: 3. Check System Tools (Tesseract & Poppler)
where tesseract >nul 2>&1
if errorlevel 1 (
    echo [NOTICE] Tesseract OCR is not found on PATH. Scanned PDF OCR will use fallbacks.
    echo          Download: https://github.com/UB-Mannheim/tesseract/wiki
) else (
    echo [OK] Tesseract OCR detected.
)

:: 4. Check & Create Python Virtual Environment
if not exist "%ROOT_DIR%.venv\Scripts\activate.bat" (
    echo [INFO] Creating Python virtual environment in .venv...
    %PY_CMD% -m venv "%ROOT_DIR%.venv"
)

call "%ROOT_DIR%.venv\Scripts\activate.bat"

:: 5. Check & Install Python Dependencies
echo [INFO] Verifying backend Python dependencies...
python -c "import fastapi, uvicorn, pydantic, sqlalchemy, pymupdf, nh3" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required Python backend dependencies from backend\requirements.txt...
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r "%ROOT_DIR%backend\requirements.txt"
    if errorlevel 1 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
    echo [OK] Backend dependencies installed successfully.
) else (
    echo [OK] Backend dependencies are already verified.
)

:: 6. Check & Install Frontend Dependencies
echo [INFO] Verifying frontend dependencies...
if not exist "%ROOT_DIR%frontend\node_modules" (
    echo [INFO] Installing frontend npm dependencies...
    cd /d "%ROOT_DIR%frontend"
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies.
        cd /d "%ROOT_DIR%"
        pause
        exit /b 1
    )
    cd /d "%ROOT_DIR%"
    echo [OK] Frontend dependencies installed successfully.
) else (
    echo [OK] Frontend dependencies are already verified.
)

:: 7. Launch Servers
echo ==========================================================================
echo   Launching Backend (Port %BACKEND_PORT%) and Frontend (Port %FRONTEND_PORT%)
echo ==========================================================================

set PYTHONPATH=%ROOT_DIR%
set VITE_BACKEND_PORT=%BACKEND_PORT%
set BACKEND_PORT=%BACKEND_PORT%
set PORT=%FRONTEND_PORT%

echo [INFO] Starting FastAPI Backend on port %BACKEND_PORT%...
start "PDF Converter Backend (%BACKEND_PORT%)" cmd /k "cd /d "%ROOT_DIR%" && call .venv\Scripts\activate.bat && uvicorn backend.app.main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"

timeout /t 2 /nobreak >nul

echo [INFO] Starting React Frontend on port %FRONTEND_PORT%...
start "PDF Converter Frontend (%FRONTEND_PORT%)" cmd /k "cd /d "%ROOT_DIR%frontend" && set VITE_BACKEND_PORT=%BACKEND_PORT% && set BACKEND_PORT=%BACKEND_PORT% && set PORT=%FRONTEND_PORT% && npm run dev -- --port %FRONTEND_PORT%"

echo.
echo ==========================================================================
echo   MULTILINGUAL PDF TO HTML PLATFORM IS RUNNING!
echo ==========================================================================
echo   Web Application:   http://localhost:%FRONTEND_PORT%
echo   REST API Docs:     http://localhost:%BACKEND_PORT%/docs
echo   Health Check:      http://localhost:%BACKEND_PORT%/api/v1/health
echo   Unique Ports:      Backend %BACKEND_PORT% ^| Frontend %FRONTEND_PORT%
echo ==========================================================================
echo Close the respective CMD windows or press any key to close this launcher.
pause

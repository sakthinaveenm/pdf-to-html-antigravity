# ==============================================================================
# Multilingual PDF to HTML Platform - Launch Script (PowerShell for Windows)
# Unique Ports:
#   - Backend API: 8844
#   - Frontend UI: 5188
# ==============================================================================

param(
    [int]$BackendPort = 8844,
    [int]$FrontendPort = 5188
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host " Starting Multilingual PDF to HTML Platform Setup & Launch" -ForegroundColor Cyan
Write-Host "   Backend Port:  $BackendPort (Unique)" -ForegroundColor Yellow
Write-Host "   Frontend Port: $FrontendPort (Unique)" -ForegroundColor Yellow
Write-Host "==========================================================================" -ForegroundColor Cyan

# 1. Search for Python 3.11+
$pyCandidates = @(
    (Join-Path $ScriptDir ".venv\Scripts\python.exe"),
    "py.exe -3.11",
    "python3.11.exe",
    "python.exe"
)

$selectedPython = $null

foreach ($cand in $pyCandidates) {
    try {
        $check = Start-Process -FilePath ($cand -split " ")[0] -ArgumentList (($cand -split " ")[1..($cand -split " ").Length] + @("-c", "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)")) -PassThru -NoNewWindow -Wait -ErrorAction SilentlyContinue
        if ($check.ExitCode -eq 0) {
            $selectedPython = $cand
            break
        }
    } catch {
        # continue searching
    }
}

if (-not $selectedPython) {
    Write-Host "[ERROR] Python 3.11 or higher is not found." -ForegroundColor Red
    Write-Host "Please install Python 3.11+: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python 3.11+ detected ($selectedPython)." -ForegroundColor Green

# 2. Check Node.js and npm
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $nodeCmd -or -not $npmCmd) {
    Write-Host "[ERROR] Node.js or npm is not installed." -ForegroundColor Red
    Write-Host "Please install Node.js 18+: https://nodejs.org/" -ForegroundColor Red
    exit 1
}
$nodeVer = & node -v
Write-Host "[OK] Node.js $nodeVer detected." -ForegroundColor Green

# 3. Check System Tools (Tesseract)
$tessCmd = Get-Command tesseract -ErrorAction SilentlyContinue
if (-not $tessCmd) {
    Write-Host "[NOTICE] Tesseract OCR is not found on PATH. Scanned PDF OCR will use fallbacks." -ForegroundColor Yellow
    Write-Host "Download: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Tesseract OCR detected." -ForegroundColor Green
}

# 4. Check & Create Virtual Environment
$venvPath = Join-Path $ScriptDir ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[INFO] Creating Python virtual environment in .venv..." -ForegroundColor Cyan
    $pyExec = ($selectedPython -split " ")[0]
    $pyArgs = ($selectedPython -split " ")[1..($selectedPython -split " ").Length] + @("-m", "venv", $venvPath)
    Start-Process -FilePath $pyExec -ArgumentList $pyArgs -Wait -NoNewWindow
}

# 5. Check & Install Python Dependencies
Write-Host "[INFO] Verifying backend Python dependencies..." -ForegroundColor Cyan
$verifyProcess = Start-Process -FilePath $venvPython -ArgumentList "-c", "import fastapi, uvicorn, pydantic, sqlalchemy, pymupdf, nh3" -PassThru -NoNewWindow -Wait -ErrorAction SilentlyContinue

if ($verifyProcess.ExitCode -ne 0) {
    Write-Host "[INFO] Installing backend dependencies from backend/requirements.txt..." -ForegroundColor Cyan
    Start-Process -FilePath $venvPython -ArgumentList "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel" -Wait -NoNewWindow
    Start-Process -FilePath $venvPython -ArgumentList "-m", "pip", "install", "-r", (Join-Path $ScriptDir "backend\requirements.txt") -Wait -NoNewWindow
    Write-Host "[OK] Backend dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[OK] Backend dependencies are already verified." -ForegroundColor Green
}

# 6. Check & Install Frontend Dependencies
$frontendDir = Join-Path $ScriptDir "frontend"
$frontendModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $frontendModules)) {
    Write-Host "[INFO] Installing frontend npm dependencies..." -ForegroundColor Cyan
    Push-Location $frontendDir
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm install" -Wait -NoNewWindow
    Pop-Location
    Write-Host "[OK] Frontend dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[OK] Frontend dependencies are already verified." -ForegroundColor Green
}

# 7. Launch Servers
Write-Host "`n[INFO] Starting FastAPI Backend on port $BackendPort..." -ForegroundColor Cyan
$env:PYTHONPATH = $ScriptDir
$backendProcess = Start-Process -FilePath $venvPython -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "$BackendPort", "--reload" -PassThru -NoNewWindow

Start-Sleep -Seconds 2

Write-Host "[INFO] Starting React Frontend on port $FrontendPort..." -ForegroundColor Cyan
$env:BACKEND_PORT = "$BackendPort"
$env:VITE_BACKEND_PORT = "$BackendPort"
$env:PORT = "$FrontendPort"

Push-Location $frontendDir
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev -- --port $FrontendPort" -PassThru -NoNewWindow
Pop-Location

Write-Host "`n==========================================================================" -ForegroundColor Green
Write-Host " MULTILINGUAL PDF TO HTML PLATFORM IS RUNNING!" -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Green
Write-Host "   Web Application:   http://localhost:$FrontendPort" -ForegroundColor Yellow
Write-Host "   REST API Docs:     http://localhost:$BackendPort/docs" -ForegroundColor Yellow
Write-Host "   Health Check:      http://localhost:$BackendPort/api/v1/health" -ForegroundColor Yellow
Write-Host "   Unique Ports:      Backend $BackendPort | Frontend $FrontendPort" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Green
Write-Host "Press Ctrl+C or close this console to terminate both servers.`n" -ForegroundColor DarkGray

try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`n[INFO] Stopping backend and frontend servers..." -ForegroundColor Yellow
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendProcess -and -not $frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Both servers stopped." -ForegroundColor Green
}

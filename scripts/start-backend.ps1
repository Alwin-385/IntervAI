# Start FastAPI backend (Windows) - uses project venv, no global uvicorn needed
param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Backend = Join-Path $Root "backend"
Set-Location $Backend

$Python = Join-Path $Backend ".venv\Scripts\python.exe"
$Alembic = Join-Path $Backend ".venv\Scripts\alembic.exe"

if (-not (Test-Path $Python)) {
    Write-Host 'Virtual environment not found. Run first-time setup:' -ForegroundColor Yellow
    Write-Host "  cd $Backend"
    Write-Host '  python -m venv .venv'
    Write-Host '  .\.venv\Scripts\pip install -r requirements.txt'
    exit 1
}

if (-not (Test-Path (Join-Path $Backend ".env"))) {
    Write-Host 'Missing backend\.env - copy from .env.example and fill in Clerk and DATABASE_URL' -ForegroundColor Red
    exit 1
}

$portInUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Port $Port is already in use. Stop the other backend terminal (Ctrl+C) or run:" -ForegroundColor Yellow
    Write-Host "  .\scripts\start-backend.ps1 -Port 8001" -ForegroundColor Yellow
    Write-Host 'Then set NEXT_PUBLIC_API_URL=http://localhost:8001 in frontend\.env.local and restart npm run dev' -ForegroundColor Yellow
    exit 1
}

Write-Host 'Running database migrations...' -ForegroundColor Cyan
& $Alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Migration failed. Is Postgres running?' -ForegroundColor Red
    Write-Host '  cd c:\IntervAI' -ForegroundColor Yellow
    Write-Host '  docker compose up -d postgres redis' -ForegroundColor Yellow
    exit $LASTEXITCODE
}

$healthUrl = "http://127.0.0.1:$Port/api/v1/health"
Write-Host "Starting API on $healthUrl" -ForegroundColor Green
Write-Host "Stop: Ctrl+C in this terminal, or run .\scripts\stop-backend.ps1 (kills port $Port + reload workers)" -ForegroundColor DarkGray
Write-Host "Frontend should use NEXT_PUBLIC_API_URL=http://127.0.0.1:$Port (see frontend\.env.local)" -ForegroundColor DarkGray
& $Python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $Port

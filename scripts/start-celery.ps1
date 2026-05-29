# Start Celery worker for all background job queues (Phase 18)
$ErrorActionPreference = "Stop"
$Backend = Join-Path (Split-Path $PSScriptRoot -Parent) "backend"
Set-Location $Backend

$Python = Join-Path $Backend ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Virtual environment not found. Run backend setup first." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $Backend ".env"))) {
    Write-Host "Missing backend\.env" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Celery worker (queues: default, resume, interview, ai)..." -ForegroundColor Green
& $Python -m celery -A app.workers.celery_app worker --loglevel=info -Q default,resume,interview,ai

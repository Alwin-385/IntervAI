# Start infrastructure services for local development
param(
    [switch]$InfraOnly
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Starting Postgres, Redis, and Qdrant..." -ForegroundColor Cyan
Write-Host "(Requires Docker Desktop to be running.)" -ForegroundColor DarkGray
docker compose up -d postgres redis qdrant
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker failed. Open Docker Desktop, wait until it is ready, then run this script again." -ForegroundColor Red
    exit $LASTEXITCODE
}

if ($InfraOnly) {
    Write-Host "Infrastructure is running." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Next steps (use two more terminals):" -ForegroundColor Yellow
Write-Host "  Backend:  .\scripts\start-backend.ps1"
Write-Host "  Frontend: .\scripts\start-frontend.ps1"
Write-Host "  Status:   .\scripts\dev-status.ps1"
Write-Host ""
Write-Host "Full guide: docs\RUN-LOCAL-WINDOWS.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Manual backend (if script fails):" -ForegroundColor DarkYellow
Write-Host "  cd backend"
Write-Host "  .\.venv\Scripts\alembic upgrade head"
Write-Host "  .\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"
Write-Host ""
Write-Host "Full guide: docs\TESTING.md" -ForegroundColor Cyan

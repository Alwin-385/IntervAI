# Start infrastructure services for local development
param(
    [switch]$InfraOnly
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Starting Postgres, Redis, and Qdrant..." -ForegroundColor Cyan
docker compose up -d postgres redis qdrant

if ($InfraOnly) {
    Write-Host "Infrastructure is running." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  Backend:  cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload"
Write-Host "  Frontend: cd frontend; npm install; npm run dev"

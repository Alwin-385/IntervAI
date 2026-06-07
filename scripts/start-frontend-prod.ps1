# Run frontend in production mode locally (fast navigation — no per-route dev compile)
param(
    [switch]$KillStalePort
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Frontend = Join-Path $Root "frontend"
Set-Location $Frontend

if (-not (Test-Path (Join-Path $Frontend ".env.local"))) {
    Write-Host 'Missing frontend\.env.local - copy from .env.example and add Clerk keys' -ForegroundColor Red
    exit 1
}

$portBlocker = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($portBlocker) {
    if ($KillStalePort) {
        Stop-Process -Id $portBlocker.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Port 3000 is in use. Stop dev server or run with -KillStalePort" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Building frontend (one-time, ~1-2 min)..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Starting production server at http://localhost:3000" -ForegroundColor Green
Write-Host "Navigation is instant. Re-run this script after code changes." -ForegroundColor DarkGray
Write-Host ""
npm run start -- --port 3000

# Start Next.js frontend (Windows) — always tries port 3000 first
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

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    Write-Host 'Installing npm dependencies...' -ForegroundColor Cyan
    npm install
}

$portBlocker = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($portBlocker) {
    $blockerPid = $portBlocker.OwningProcess
    $blockerName = (Get-Process -Id $blockerPid -ErrorAction SilentlyContinue).ProcessName
    Write-Host "Port 3000 is in use (PID $blockerPid, $blockerName)." -ForegroundColor Yellow
    if ($KillStalePort) {
        Write-Host "Stopping PID $blockerPid ..." -ForegroundColor Yellow
        Stop-Process -Id $blockerPid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    } else {
        Write-Host ""
        Write-Host "OPTION A — use the app already running:" -ForegroundColor Cyan
        Write-Host "  Open  http://localhost:3000" -ForegroundColor White
        Write-Host ""
        Write-Host "OPTION B — restart frontend on 3000:" -ForegroundColor Cyan
        Write-Host "  .\scripts\start-frontend.ps1 -KillStalePort" -ForegroundColor White
        Write-Host "  Or:  taskkill /PID $blockerPid /F" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

Write-Host ""
Write-Host "Starting frontend at  http://localhost:3000" -ForegroundColor Green
Write-Host "Keep this window open. Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

# Do not pass --hostname 127.0.0.1: browsing via localhost:3000 causes a proxy loop (500 error).
npm run dev -- --port 3000

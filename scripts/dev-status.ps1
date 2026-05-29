# Show which IntervAI services are running and which URLs to open
$ErrorActionPreference = "SilentlyContinue"

function Test-PortListen([int]$Port) {
    $c = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $c) { return $null }
    $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
    return [PSCustomObject]@{ Port = $Port; PID = $c.OwningProcess; Name = $proc.ProcessName }
}

Write-Host ""
Write-Host "IntervAI local dev status" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

$pg = docker ps --filter "name=intervai-postgres" --format "{{.Status}}" 2>$null
$redis = docker ps --filter "name=intervai-redis" --format "{{.Status}}" 2>$null
Write-Host "Docker Postgres: $(if ($pg) { $pg } else { 'not running — run: docker compose up -d postgres redis' })"
Write-Host "Docker Redis:    $(if ($redis) { $redis } else { 'not running' })"

$api = Test-PortListen 8000
$fe0 = Test-PortListen 3000
$fe1 = Test-PortListen 3001

if ($api) {
    Write-Host "Backend API:     RUNNING  PID $($api.PID)  ->  http://localhost:8000/api/v1/health" -ForegroundColor Green
} else {
    Write-Host "Backend API:     STOPPED  ->  .\scripts\start-backend.ps1" -ForegroundColor Red
}

if ($fe0) {
    Write-Host "Frontend:        RUNNING  PID $($fe0.PID)  ->  http://localhost:3000" -ForegroundColor Green
} elseif ($fe1) {
    Write-Host "Frontend:        RUNNING  PID $($fe1.PID)  ->  http://localhost:3001" -ForegroundColor Green
} else {
    Write-Host "Frontend:        STOPPED  ->  .\scripts\start-frontend.ps1" -ForegroundColor Red
}

if ($fe1 -and -not $fe0) {
    Write-Host ""
    Write-Host "Note: Only port 3001 is active. Use http://localhost:3001 (not 3000)." -ForegroundColor Yellow
}
if ($fe0 -and -not $fe1) {
    Write-Host ""
    Write-Host "Note: App is on port 3000. Do NOT use http://localhost:3001 unless Next.js moved there." -ForegroundColor Yellow
}

try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health" -UseBasicParsing -TimeoutSec 2
    Write-Host "Health check:    OK ($($r.StatusCode))" -ForegroundColor Green
} catch {
    if ($api) {
        Write-Host "Health check:    API port open but /health failed - check backend logs" -ForegroundColor Yellow
    }
}

Write-Host ""

# Stop FastAPI backend on Windows (uvicorn --reload leaves orphan child processes)
param(
    [int]$Port = 8000
)

$ErrorActionPreference = "SilentlyContinue"
$Root = Split-Path $PSScriptRoot -Parent
$Backend = Join-Path $Root "backend"

$killed = @()

function Stop-ProcessTree {
    param([int]$ProcessId)
    if ($ProcessId -le 0) { return }
    $null = taskkill /PID $ProcessId /F /T 2>&1
    if ($LASTEXITCODE -eq 0) {
        $script:killed += $ProcessId
    }
}

# 1) Whatever is listening on the API port
$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $listeners) {
    Stop-ProcessTree -ProcessId $conn.OwningProcess
}

# 2) Orphan uvicorn / reload workers for this project
Get-CimInstance Win32_Process -Filter "name='python.exe'" | ForEach-Object {
    $cmd = $_.CommandLine
    if (-not $cmd) { return }
    if ($cmd -notmatch "uvicorn") { return }
    if ($cmd -notmatch [regex]::Escape($Backend)) { return }
    Stop-ProcessTree -ProcessId $_.ProcessId
}

Start-Sleep -Milliseconds 500
$stillListening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($stillListening) {
    Write-Host "Port $Port is still in use (PID $($stillListening.OwningProcess))." -ForegroundColor Red
    Write-Host "Close the terminal running start-backend.ps1, or run as admin:" -ForegroundColor Yellow
    Write-Host "  taskkill /PID $($stillListening.OwningProcess) /F /T" -ForegroundColor Yellow
    exit 1
}

if ($killed.Count -gt 0) {
    Write-Host "Stopped backend on port $Port (PIDs: $($killed -join ', '))." -ForegroundColor Green
} else {
    Write-Host "No backend process found on port $Port." -ForegroundColor DarkGray
}

exit 0

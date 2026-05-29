# Re-run extraction for all resumes stuck in 'queued' (one-time fix after bugs)
$ErrorActionPreference = "Stop"
$Backend = Join-Path (Split-Path $PSScriptRoot -Parent) "backend"
Set-Location $Backend

$Python = Join-Path $Backend ".venv\Scripts\python.exe"
& $Python -c @"
from app.services.resume_stale_recovery import recover_stale_queued_resumes
count = recover_stale_queued_resumes(max_age_seconds=0)
print(f'Started extraction for {count} queued resume(s).')
"@

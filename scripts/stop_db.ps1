# Stop Local PostgreSQL Server for AI Travel Planner
$ErrorActionPreference = "SilentlyContinue"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
$pgDataDir = Join-Path $projectDir "data\pgdata"
$pgBinDir = "C:\Program Files\PostgreSQL\18\bin"

Write-Host "Stopping PostgreSQL server on port 5432..." -ForegroundColor Yellow
if (Test-Path "$pgBinDir\pg_ctl.exe") {
    & "$pgBinDir\pg_ctl.exe" -D "$pgDataDir" -m fast stop
}

# Kill any lingering postgres process listening on port 5432
$conn = Get-NetTCPConnection -LocalPort 5432 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host "PostgreSQL server stopped." -ForegroundColor Green

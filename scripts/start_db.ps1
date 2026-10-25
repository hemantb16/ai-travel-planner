# Start Local PostgreSQL Server for AI Travel Planner
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
$pgDataDir = Join-Path $projectDir "data\pgdata"
$pgBinDir = "C:\Program Files\PostgreSQL\18\bin"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Starting Local PostgreSQL 18 Server   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if port 5432 is already listening
$tcp = Get-NetTCPConnection -LocalPort 5432 -State Listen -ErrorAction SilentlyContinue
if ($tcp) {
    Write-Host "PostgreSQL is already running on port 5432." -ForegroundColor Green
    exit 0
}

# If pgdata does not exist, initialize it
if (-not (Test-Path $pgDataDir)) {
    Write-Host "Initializing new database cluster at $pgDataDir..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path (Split-Path -Parent $pgDataDir) -Force | Out-Null
    & "$pgBinDir\initdb.exe" -D "$pgDataDir" -U postgres -A trust --encoding=UTF8
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to initialize PostgreSQL database cluster."
        exit 1
    }
}

# Start PostgreSQL server in background
Write-Host "Starting postgres.exe on port 5432..." -ForegroundColor Yellow
Start-Process -FilePath "$pgBinDir\postgres.exe" -ArgumentList "-D", "$pgDataDir", "-p", "5432" -WindowStyle Hidden

# Wait for server to become responsive
$started = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    $tcp = Get-NetTCPConnection -LocalPort 5432 -State Listen -ErrorAction SilentlyContinue
    if ($tcp) {
        $started = $true
        break
    }
}

if ($started) {
    Write-Host "PostgreSQL 18 is online on port 5432!" -ForegroundColor Green
    
    # Ensure travel_planner database exists
    $dbCheck = & "$pgBinDir\psql.exe" -h 127.0.0.1 -p 5432 -U postgres -lqt 2>$null | Select-String "travel_planner"
    if (-not $dbCheck) {
        Write-Host "Creating database 'travel_planner'..." -ForegroundColor Yellow
        & "$pgBinDir\createdb.exe" -h 127.0.0.1 -p 5432 -U postgres travel_planner
        Write-Host "Database 'travel_planner' created." -ForegroundColor Green
    }
} else {
    Write-Warning "PostgreSQL took longer than expected to start. Check $pgDataDir\logfile.log"
}

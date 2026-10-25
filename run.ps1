# Wanderlust AI Travel Planner Launcher
$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       Wanderlust AI — Local Travel Concierge             " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Database
Write-Host "[1/3] Checking PostgreSQL 18 database..." -ForegroundColor Yellow
& "$projectDir\scripts\start_db.ps1"

# 2. Check Ollama
Write-Host "[2/3] Checking Ollama AI engine..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    $modelCount = $ollamaCheck.models.Count
    Write-Host "Ollama is online with $modelCount installed models." -ForegroundColor Green
} catch {
    Write-Warning "Ollama is not responding at http://127.0.0.1:11434. Starting Ollama in the background..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

# 3. Launch App
Write-Host "[3/3] Launching FastAPI Web Application..." -ForegroundColor Yellow
$venvPython = "$projectDir\.venv\Scripts\python.exe"

# Open browser after 2 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
} | Out-Null

Write-Host "`nApp running at http://127.0.0.1:8000 (Press Ctrl+C to stop)`n" -ForegroundColor Green
& $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000

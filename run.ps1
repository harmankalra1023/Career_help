<#
.SYNOPSIS
    Starts both the Digital Career Twin FastAPI Backend and Next.js Frontend.
.EXAMPLE
    .\run.ps1
#>

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Starting Digital Career Twin (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Add Node.js to PATH if present in standard location
if (Test-Path "C:\Program Files\nodejs") {
    $env:Path = "C:\Program Files\nodejs;" + $env:Path
}

# Locate Python
$pythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "`n[1/2] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting Backend API...' -ForegroundColor Green; & '$pythonExe' -m uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[2/2] Launching Next.js Frontend on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting Frontend Web...' -ForegroundColor Green; Set-Location 'apps/web'; & 'C:\Program Files\nodejs\npm.cmd' run dev"

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "Both services are booting up in separate terminals!" -ForegroundColor Green
Write-Host "  - Web Frontend:  http://localhost:3000" -ForegroundColor Yellow
Write-Host "  - Backend Docs:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  - Health Check:  http://localhost:8000/healthz" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

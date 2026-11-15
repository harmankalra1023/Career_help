@echo off
title Digital Career Twin Runner
echo ===================================================
echo     Starting Digital Career Twin (Backend + Frontend)
echo ===================================================
echo.

:: Detect Python environment
set "PYTHON_EXE=.\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: Ensure Node.js is on PATH if in default install directory
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    if exist "C:\Program Files\nodejs\node.exe" (
        set "PATH=%PATH%;C:\Program Files\nodejs"
    )
)

echo [1/2] Launching FastAPI Backend on http://localhost:8000 ...
start "DCT Backend API" cmd /k "title DCT Backend API & %PYTHON_EXE% -m uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo [2/2] Launching Next.js Frontend on http://localhost:3000 ...
start "DCT Frontend Web" cmd /k "title DCT Frontend Web & cd apps\web && npm run dev"

echo.
echo ===================================================
echo Both services are booting up in separate terminals!
echo.
echo   - Web Frontend:  http://localhost:3000
echo   - Backend Docs:  http://localhost:8000/docs
echo   - Health Check:  http://localhost:8000/healthz
echo ===================================================
echo.
pause

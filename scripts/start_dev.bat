@echo off
REM Script to start both Flask backend and Next.js frontend (Windows)

echo 🚀 Starting development servers...
echo.

REM Get the project root directory
set PROJECT_ROOT=%~dp0..
set BACKEND_DIR=%PROJECT_ROOT%\src
set FRONTEND_DIR=%PROJECT_ROOT%\..\NextJs-Super-FrontEnd

REM Check if frontend directory exists
if not exist "%FRONTEND_DIR%" (
    echo ⚠️  Frontend directory not found at: %FRONTEND_DIR%
    echo    Starting backend only...
    echo.
    cd /d "%BACKEND_DIR%"
    call .venv\Scripts\activate.bat
    python app.py
    exit /b 0
)

REM Start Flask backend in new window
echo 📦 Starting Flask backend...
start "Flask Backend" cmd /k "cd /d %BACKEND_DIR% && .venv\Scripts\activate.bat && python app.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start Next.js frontend in new window
echo 🌐 Starting Next.js frontend...
start "Next.js Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✨ Development servers are running!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Backend:  http://localhost:4000
echo Frontend: http://localhost:3000
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Close the windows to stop the servers
pause


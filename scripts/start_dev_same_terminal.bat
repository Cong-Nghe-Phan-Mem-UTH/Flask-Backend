@echo off
REM Script to start both Flask backend and Next.js frontend in the same terminal (Windows)
REM This version runs both processes in the background of the same terminal

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

REM Check if virtual environment exists
if not exist "%BACKEND_DIR%\.venv" (
    echo ⚠️  Virtual environment not found. Creating...
    cd /d "%BACKEND_DIR%"
    python -m venv .venv
)

REM Check if dependencies are installed
cd /d "%BACKEND_DIR%"
call .venv\Scripts\activate.bat
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing backend dependencies...
    pip install -r requirements.txt
)

REM Start Flask backend in background
echo 📦 Starting Flask backend...
start /b "" cmd /c "cd /d %BACKEND_DIR% && .venv\Scripts\activate.bat && python app.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Check if node_modules exists
if not exist "%FRONTEND_DIR%\node_modules" (
    echo ⚠️  Installing frontend dependencies...
    cd /d "%FRONTEND_DIR%"
    call npm install
)

REM Start Next.js frontend in background
echo 🌐 Starting Next.js frontend...
start /b "" cmd /c "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✨ Development servers are running!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Backend:  http://localhost:4000
echo Frontend: http://localhost:3000
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Press Ctrl+C to stop all servers
echo Note: Output from both servers will appear in this terminal
echo.

REM Keep the script running
:loop
timeout /t 1 /nobreak >nul
goto loop



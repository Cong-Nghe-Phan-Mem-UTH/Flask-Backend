# PowerShell script to start both Flask backend and Next.js frontend
# Usage: .\scripts\start_dev.ps1
# Or: powershell -ExecutionPolicy Bypass -File scripts\start_dev.ps1

Write-Host "🚀 Starting development servers..." -ForegroundColor Cyan
Write-Host ""

# Get the project root directory
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$BACKEND_DIR = Join-Path $PROJECT_ROOT "src"
$FRONTEND_DIR = Join-Path (Split-Path -Parent $PROJECT_ROOT) "NextJs-Super-FrontEnd"

# Check if frontend directory exists
if (-not (Test-Path $FRONTEND_DIR)) {
    Write-Host "⚠️  Frontend directory not found at: $FRONTEND_DIR" -ForegroundColor Yellow
    Write-Host "   Starting backend only..." -ForegroundColor Yellow
    Write-Host ""
    Set-Location $BACKEND_DIR
    & .\.venv\Scripts\Activate.ps1
    python app.py
    exit 0
}

# Check if virtual environment exists
if (-not (Test-Path (Join-Path $BACKEND_DIR ".venv"))) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    Set-Location $BACKEND_DIR
    python -m venv .venv
}

# Check if dependencies are installed
Set-Location $BACKEND_DIR
try {
    & .\.venv\Scripts\python.exe -c "import flask" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Installing backend dependencies..." -ForegroundColor Yellow
        & .\.venv\Scripts\pip.exe install -r requirements.txt
    }
} catch {
    Write-Host "⚠️  Installing backend dependencies..." -ForegroundColor Yellow
    & .\.venv\Scripts\pip.exe install -r requirements.txt
}

# Function to cleanup on exit
$script:backendProcess = $null
$script:frontendProcess = $null

function Cleanup {
    Write-Host ""
    Write-Host "🛑 Stopping servers..." -ForegroundColor Yellow
    if ($script:backendProcess -and -not $script:backendProcess.HasExited) {
        Stop-Process -Id $script:backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($script:frontendProcess -and -not $script:frontendProcess.HasExited) {
        Stop-Process -Id $script:frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

# Register cleanup on Ctrl+C
[Console]::TreatControlCAsInput = $false
Register-ObjectEvent -InputObject ([System.Console]) -EventName "CancelKeyPress" -Action { Cleanup; exit } | Out-Null

# Start Flask backend
Write-Host "📦 Starting Flask backend..." -ForegroundColor Green
$backendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
$backendStartInfo.FileName = "cmd.exe"
$backendStartInfo.Arguments = "/c `"cd /d `"$BACKEND_DIR`" && .venv\Scripts\activate.bat && python app.py`""
$backendStartInfo.UseShellExecute = $false
$backendStartInfo.RedirectStandardOutput = $true
$backendStartInfo.RedirectStandardError = $true
$backendStartInfo.CreateNoWindow = $false
$script:backendProcess = [System.Diagnostics.Process]::Start($backendStartInfo)

Write-Host "✅ Backend started (PID: $($script:backendProcess.Id))" -ForegroundColor Green
Write-Host ""

# Wait a bit for backend to start
Start-Sleep -Seconds 2

# Check if node_modules exists
if (-not (Test-Path (Join-Path $FRONTEND_DIR "node_modules"))) {
    Write-Host "⚠️  Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location $FRONTEND_DIR
    npm install
}

# Start Next.js frontend
Write-Host "🌐 Starting Next.js frontend..." -ForegroundColor Green
$frontendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
$frontendStartInfo.FileName = "cmd.exe"
$frontendStartInfo.Arguments = "/c `"cd /d `"$FRONTEND_DIR`" && npm run dev`""
$frontendStartInfo.UseShellExecute = $false
$frontendStartInfo.RedirectStandardOutput = $true
$frontendStartInfo.RedirectStandardError = $true
$frontendStartInfo.CreateNoWindow = $false
$script:frontendProcess = [System.Diagnostics.Process]::Start($frontendStartInfo)

Write-Host "✅ Frontend started (PID: $($script:frontendProcess.Id))" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✨ Development servers are running!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:4000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Wait for processes
try {
    Wait-Process -Id $script:backendProcess.Id, $script:frontendProcess.Id -ErrorAction SilentlyContinue
} catch {
    # One or both processes may have exited
}
finally {
    Cleanup
}


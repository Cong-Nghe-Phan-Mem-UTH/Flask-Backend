@echo off
REM Start Database Studio (Prisma Studio style) on port 5555

cd /d "%~dp0\..\src"

echo 🚀 Starting Database Studio...
echo 📊 Access at: http://localhost:5555
echo 🔐 Login with Owner account
echo.

python admin_studio.py

pause


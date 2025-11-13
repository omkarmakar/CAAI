@echo off
echo ========================================
echo  CAAI Dashboard - Quick Start
echo ========================================
echo.

echo [1/2] Starting Backend Server...
start cmd /k "cd backend && python main.py"
timeout /t 5 /nobreak > nul

echo [2/2] Starting Dashboard...
start cmd /k "cd frontend-dashboard && npm run dev"
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo  CAAI Dashboard Started Successfully!
echo ========================================
echo.
echo Backend:   http://localhost:8000
echo Dashboard: http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul
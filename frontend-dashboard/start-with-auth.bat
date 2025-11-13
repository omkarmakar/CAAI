@echo off
echo ================================================
echo CAAI Dashboard - Quick Start with Authentication
echo ================================================
echo.
echo This will:
echo 1. Start the backend (FastAPI) on port 8000
echo 2. Start the dashboard (Next.js) on port 3000
echo 3. Open browser to http://localhost:3000
echo.
echo ================================================
echo FIRST TIME USERS:
echo ================================================
echo When dashboard opens:
echo 1. Click "Login" button (top-right)
echo 2. Click "Don't have an account? Register"
echo 3. Fill in your details:
echo    - Username: your_username
echo    - Email: your@email.com
echo    - Password: (min 6 characters)
echo    - Role: ca (recommended) or user/senior_ca/admin
echo 4. After registration, login with your credentials
echo.
echo ================================================
echo FILE UPLOAD FEATURE:
echo ================================================
echo To use file upload:
echo 1. Login first
echo 2. Click "Execute Agent" on any agent card
echo 3. Select an action
echo 4. Look for file upload parameters (📁 icon)
echo 5. Click upload area and choose file
echo 6. Wait for ✓ confirmation
echo 7. Click "Execute Agent"
echo.
echo ================================================
pause

echo.
echo Starting backend server...
start "CAAI Backend" cmd /k "cd ..\backend && python main.py"

timeout /t 3 /nobreak

echo Starting frontend dashboard...
start "CAAI Dashboard" cmd /k "cd . && npm run dev"

timeout /t 5 /nobreak

echo Opening browser...
start http://localhost:3000

echo.
echo ================================================
echo Dashboard is starting...
echo ================================================
echo Backend:   http://localhost:8000
echo Dashboard: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause
taskkill /FI "WindowTitle eq CAAI Backend*" /T /F
taskkill /FI "WindowTitle eq CAAI Dashboard*" /T /F
echo.
echo All servers stopped.
pause

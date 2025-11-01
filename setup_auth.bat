@echo off
REM CAAI Authentication Setup Script for Windows
echo 🚀 Setting up CAAI Authentication System...
echo ============================================================

REM Backend setup
echo 📦 Installing Python dependencies...
cd backend
pip install -r requirements.txt

echo 🗄️ Initializing authentication database...
python init_auth_db.py

REM Frontend setup
echo 📦 Installing Node.js dependencies...
cd ..\frontend-next
npm install

REM Create environment files
echo ⚙️ Creating environment files...

REM Backend .env
echo # JWT Configuration > ..\backend\.env
echo JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-%RANDOM%-%RANDOM% >> ..\backend\.env
echo. >> ..\backend\.env
echo # Database >> ..\backend\.env
echo DATABASE_URL=sqlite:///./caai_auth.db >> ..\backend\.env
echo. >> ..\backend\.env
echo # FastAPI >> ..\backend\.env
echo UVICORN_HOST=0.0.0.0 >> ..\backend\.env
echo UVICORN_PORT=8000 >> ..\backend\.env
echo. >> ..\backend\.env
echo # Gemini API >> ..\backend\.env
echo GEMINI_API_KEY=AIzaSyATL5uTTApzOo7m6bItJPCP1IV8f3VGXKk >> ..\backend\.env

REM Frontend .env.local
echo # API Configuration > .env.local
echo NEXT_PUBLIC_API_URL=http://localhost:8000 >> .env.local

echo.
echo ============================================================
echo ✅ CAAI Authentication System Setup Complete!
echo.
echo 📋 Summary:
echo    • Python dependencies installed
echo    • Authentication database initialized
echo    • Node.js dependencies installed
echo    • Environment files created
echo.
echo 🚀 To start the system:
echo    Backend:  cd backend ^& python main.py
echo    Frontend: cd frontend-next ^& npm run dev
echo.
echo 🔐 Default accounts created:
echo    SuperAdmin: superadmin / SuperAdmin@123
echo    Admin:      admin / Admin@123
echo    User:       user1 / User@123
echo.
echo ⚠️  Security Reminders:
echo    • Change default passwords immediately
echo    • Update JWT_SECRET_KEY in production
echo    • Enable HTTPS in production
echo    • Configure proper CORS origins

pause
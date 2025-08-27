@echo off
REM IPAM Tool - Automated Setup Script for Windows (Batch version)
REM This script automates the complete setup process for the IPAM tool
REM Run this script from the root directory of the ipam-tool repository

echo.
echo 🚀 IPAM Tool - Automated Setup Script
echo =====================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Backend directory not found. Please run this script from the ipam-tool root directory.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Frontend directory not found. Please run this script from the ipam-tool root directory.
    pause
    exit /b 1
)

echo 📋 Setting up Backend...
cd backend

REM Create backend .env file
echo 📝 Creating backend .env file...
(
echo DATABASE_URL=sqlite+aiosqlite:///./ipam.db
echo JWT_SECRET_KEY=your-secret-key-here-change-in-production
echo JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here-change-in-production
echo ACCESS_TOKEN_EXPIRE_MINUTES=15
echo REFRESH_TOKEN_EXPIRE_DAYS=7
echo ADMIN_EMAIL=admin@example.com
echo ADMIN_PASSWORD=changeme123!
echo CORS_ORIGINS=http://localhost:5173,http://localhost:5174
echo ENV=development
echo LOG_LEVEL=info
) > .env

echo ✅ Backend .env file created

REM Install backend dependencies
echo 📦 Installing backend dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed

REM Initialize database
echo 🗄️ Initializing database...
python init_db.py
if errorlevel 1 (
    echo ❌ Failed to initialize database
    pause
    exit /b 1
)
echo ✅ Database initialized

python create_admin.py
if errorlevel 1 (
    echo ❌ Failed to create admin user
    pause
    exit /b 1
)
echo ✅ Admin user created

REM Start backend server
echo 🚀 Starting backend server...
start "IPAM Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 5 /nobreak > nul

REM Setup frontend
echo.
echo ⚛️ Setting up Frontend...
cd ..\frontend

REM Create frontend .env.local file
echo 📝 Creating frontend .env.local file...
echo VITE_API_BASE=http://localhost:8000/api > .env.local
echo ✅ Frontend .env.local file created

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
npm install
if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed

REM Start frontend server
echo 🚀 Starting frontend server...
start "IPAM Frontend" cmd /k "npm run dev"

REM Wait for frontend to start
timeout /t 10 /nobreak > nul

REM Open browser
echo.
echo 🌐 Opening browser...
start http://localhost:5173

echo.
echo 🎉 IPAM Tool Setup Complete!
echo ================================
echo.
echo 🔗 Frontend URL: http://localhost:5173
echo 🔗 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 🔐 Login Credentials:
echo    Email: admin@example.com
echo    Password: changeme123!
echo.
echo ✨ Features Available:
echo    • Manual CIDR allocation
echo    • Auto allocation by subnet mask
echo    • Auto allocation by host count
echo    • Flexible gateway assignment options
echo.
echo ⚠️  Both servers are running in separate windows.
echo    Close those windows to stop the servers.
echo.
pause

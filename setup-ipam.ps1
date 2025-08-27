# IPAM Tool - Automated Setup Script for Windows
# This script automates the complete setup process for the IPAM tool
# Run this script from the root directory of the ipam-tool repository

param(
    [switch]$SkipDependencies,
    [switch]$SkipDatabase,
    [string]$AdminEmail = "admin@example.com",
    [string]$AdminPassword = "changeme123!"
)

Write-Host "🚀 IPAM Tool - Automated Setup Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to wait for server to be ready
function Wait-ForServer($url, $timeout = 60) {
    $elapsed = 0
    Write-Host "⏳ Waiting for server at $url to be ready..." -ForegroundColor Yellow
    
    do {
        try {
            $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Server is ready!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Start-Sleep -Seconds 2
            $elapsed += 2
        }
    } while ($elapsed -lt $timeout)
    
    Write-Host "❌ Server failed to start within $timeout seconds" -ForegroundColor Red
    return $false
}

# Check prerequisites
Write-Host "`n📋 Checking Prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "node")) {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 16+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "npm")) {
    Write-Host "❌ npm is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All prerequisites found" -ForegroundColor Green

# Backend Setup
Write-Host "`n🐍 Setting up Backend..." -ForegroundColor Yellow

if (-not (Test-Path "backend")) {
    Write-Host "❌ Backend directory not found. Please run this script from the ipam-tool root directory." -ForegroundColor Red
    exit 1
}

Set-Location "backend"

# Create backend .env file
Write-Host "📝 Creating backend .env file..." -ForegroundColor Cyan
$backendEnv = @"
DATABASE_URL=sqlite+aiosqlite:///./ipam.db
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ADMIN_EMAIL=$AdminEmail
ADMIN_PASSWORD=$AdminPassword
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
ENV=development
LOG_LEVEL=info
"@

$backendEnv | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Backend .env file created" -ForegroundColor Green

# Install backend dependencies
if (-not $SkipDependencies) {
    Write-Host "📦 Installing backend dependencies..." -ForegroundColor Cyan
    try {
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
        Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to install backend dependencies: $_" -ForegroundColor Red
        exit 1
    }
}

# Initialize database
if (-not $SkipDatabase) {
    Write-Host "🗄️ Initializing database..." -ForegroundColor Cyan
    try {
        python init_db.py
        if ($LASTEXITCODE -ne 0) { throw "Database initialization failed" }
        Write-Host "✅ Database initialized" -ForegroundColor Green
        
        python create_admin.py
        if ($LASTEXITCODE -ne 0) { throw "Admin user creation failed" }
        Write-Host "✅ Admin user created" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to initialize database: $_" -ForegroundColor Red
        exit 1
    }
}

# Start backend server in background
Write-Host "🚀 Starting backend server..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Frontend Setup
Write-Host "`n⚛️ Setting up Frontend..." -ForegroundColor Yellow
Set-Location "../frontend"

# Create frontend .env.local file
Write-Host "📝 Creating frontend .env.local file..." -ForegroundColor Cyan
"VITE_API_BASE=http://localhost:8000/api" | Out-File -FilePath ".env.local" -Encoding UTF8
Write-Host "✅ Frontend .env.local file created" -ForegroundColor Green

# Install frontend dependencies
if (-not $SkipDependencies) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Cyan
    try {
        npm install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
        Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to install frontend dependencies: $_" -ForegroundColor Red
        Stop-Job $backendJob -Force
        exit 1
    }
}

# Wait for backend to be ready
if (-not (Wait-ForServer "http://localhost:8000/healthz" 30)) {
    Write-Host "❌ Backend server failed to start" -ForegroundColor Red
    Stop-Job $backendJob -Force
    exit 1
}

# Start frontend server in background
Write-Host "🚀 Starting frontend server..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev
}

# Wait for frontend to be ready
if (-not (Wait-ForServer "http://localhost:5173" 30)) {
    Write-Host "❌ Frontend server failed to start" -ForegroundColor Red
    Stop-Job $backendJob -Force
    Stop-Job $frontendJob -Force
    exit 1
}

# Open browser
Write-Host "`n🌐 Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

# Display success message
Write-Host "`n🎉 IPAM Tool Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Frontend URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔗 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Login Credentials:" -ForegroundColor Yellow
Write-Host "   Email: $AdminEmail" -ForegroundColor White
Write-Host "   Password: $AdminPassword" -ForegroundColor White
Write-Host ""
Write-Host "✨ Features Available:" -ForegroundColor Yellow
Write-Host "   • Manual CIDR allocation" -ForegroundColor White
Write-Host "   • Auto allocation by subnet mask" -ForegroundColor White
Write-Host "   • Auto allocation by host count" -ForegroundColor White
Write-Host "   • Flexible gateway assignment options" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Both servers are running in background jobs." -ForegroundColor Yellow
Write-Host "   To stop servers, close this PowerShell window or run:" -ForegroundColor Yellow
Write-Host "   Get-Job | Stop-Job -Force" -ForegroundColor White
Write-Host ""

# Keep script running to maintain background jobs
Write-Host "Press Ctrl+C to stop all servers and exit..." -ForegroundColor Yellow
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check if jobs are still running
        if ((Get-Job -Id $backendJob.Id).State -eq "Failed") {
            Write-Host "❌ Backend server stopped unexpectedly" -ForegroundColor Red
            break
        }
        if ((Get-Job -Id $frontendJob.Id).State -eq "Failed") {
            Write-Host "❌ Frontend server stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
}
catch {
    Write-Host "`n🛑 Stopping servers..." -ForegroundColor Yellow
}
finally {
    Stop-Job $backendJob -Force -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -Force -ErrorAction SilentlyContinue
    Remove-Job $backendJob -Force -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -Force -ErrorAction SilentlyContinue
    Write-Host "✅ All servers stopped" -ForegroundColor Green
}

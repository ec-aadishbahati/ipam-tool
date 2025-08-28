# 🚀 IPAM Tool - Quick Setup Guide

This guide provides automated setup scripts to get the IPAM tool running quickly on Windows systems.

## 📋 Prerequisites

Before running the setup scripts, ensure you have:

- **Python 3.8+** installed and added to PATH
- **Node.js 16+** installed and added to PATH
- **Git** for cloning the repository

## 🔧 Automated Setup Options

### Option 1: PowerShell Script (Recommended)

The PowerShell script provides advanced features like error handling, server health checks, and background job management.

```powershell
# Run from the ipam-tool root directory
.\setup-ipam.ps1
```

**Advanced Usage:**
```powershell
# Skip dependency installation (if already installed)
.\setup-ipam.ps1 -SkipDependencies

# Skip database initialization (if already done)
.\setup-ipam.ps1 -SkipDatabase

# Custom admin credentials
.\setup-ipam.ps1 -AdminEmail "your@email.com" -AdminPassword "yourpassword"

# Combine options
.\setup-ipam.ps1 -SkipDependencies -AdminEmail "admin@company.com"
```

### Option 2: Batch File (Simple)

For users who prefer cmd or have PowerShell execution policy restrictions:

```cmd
# Run from the ipam-tool root directory
setup-ipam.bat
```

## 🎯 What the Scripts Do

1. **✅ Check Prerequisites** - Verify Python and Node.js are installed
2. **🐍 Backend Setup:**
   - Create `.env` file with database and authentication settings
   - Install Python dependencies from `requirements.txt`
   - Initialize SQLite database with tables
   - Create admin user account
   - Start backend server on `http://localhost:8000`

3. **⚛️ Frontend Setup:**
   - Create `.env.local` file with API base URL
   - Install Node.js dependencies
   - Start frontend development server on `http://localhost:5173`

4. **🌐 Launch Application:**
   - Wait for servers to be ready
   - Automatically open browser to `http://localhost:5173`

## 🔐 Default Login Credentials

- **Email:** `admin@example.com`
- **Password:** Generated during setup (displayed in setup script output)

**Important:** You will be required to change the password on first login for security.

## 🌟 Available Features

After setup, you'll have access to:

- **Manual CIDR Allocation** - Enter subnet CIDR directly
- **Auto by Subnet Mask** - Specify mask (e.g., /24) to get first available subnet
- **Auto by Host Count** - Specify host count to get appropriately sized subnet
- **Gateway Assignment Options:**
  - Manual gateway IP
  - Auto first IP assignment
  - No gateway (all IPs usable)
- **Complete IPAM Management** - Supernets, Subnets, Devices, VLANs, Purposes, IP Assignments

## 🛠️ Manual Setup (Alternative)

If you prefer manual setup or encounter issues with the scripts, follow these steps:

### Backend Setup
```cmd
cd backend
pip install -r requirements.txt

# Create .env file with the content from setup scripts
python init_db.py
python create_admin.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```cmd
cd frontend
npm install

# Create .env.local with: VITE_API_BASE=http://localhost:8000/api
npm run dev
```

## 🔧 Troubleshooting

### Common Issues

**"Python is not recognized"**
- Install Python from https://python.org
- Ensure "Add Python to PATH" is checked during installation

**"Node is not recognized"**
- Install Node.js from https://nodejs.org
- Restart command prompt after installation

**"Permission denied" (PowerShell)**
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use the batch file instead

**Database errors**
- Delete `backend/ipam.db` and run the script again
- Ensure no other instances are running

**Port already in use**
- Stop any existing servers on ports 8000 or 5173
- Or modify the ports in the configuration files

### Getting Help

If you encounter issues:
1. Check that all prerequisites are installed correctly
2. Ensure you're running the script from the `ipam-tool` root directory
3. Try the manual setup steps if scripts fail
4. Check the console output for specific error messages

## 🎉 Success!

Once setup is complete, you should see:
- Backend API running at `http://localhost:8000`
- Frontend application at `http://localhost:5173`
- Browser automatically opens to the login page
- Both servers running and ready for use

The IPAM tool is now ready for managing your IP address allocations with intelligent subnet allocation capabilities!

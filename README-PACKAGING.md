# IPAM Tool - Executable Packaging

This document explains how to build the IPAM Tool as a standalone executable using Electron and PyInstaller.

## Overview

The packaging solution combines:
- **Backend**: FastAPI application packaged with PyInstaller into a standalone executable
- **Frontend**: React application built with Vite and packaged into Electron
- **Integration**: Electron manages the backend process lifecycle and serves the frontend

## Prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- Git

## Quick Build

Run the complete build process:

```bash
python build-executable.py
```

This will:
1. Build the backend executable using PyInstaller
2. Build the frontend using Vite
3. Set up Electron with both components
4. Create the final executable

## Manual Build Steps

### 1. Build Backend Executable

```bash
cd backend
pip install pyinstaller
python build_backend.py
```

This creates `backend/dist/ipam-backend.exe` (Windows) or `backend/dist/ipam-backend` (Linux/Mac).

### 2. Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates the `frontend/dist/` directory with the built React application.

### 3. Package with Electron

```bash
cd electron
npm install
npm run dist
```

This creates the final executable in `electron/dist/`.

## Development Mode

For development, you can run the Electron app without building:

```bash
cd electron
npm run dev
```

This will:
- Start the backend using Python directly
- Load the frontend from the Vite dev server
- Open developer tools

## Configuration

### Backend Configuration

The backend executable uses these environment variables:
- `DATABASE_URL`: SQLite database path (auto-configured)
- `ADMIN_EMAIL`: admin@example.com
- `ADMIN_PASSWORD`: Cisco!123
- `JWT_SECRET_KEY`: Auto-generated for production
- `CORS_ORIGINS`: Configured for Electron frontend

### Frontend Configuration

The frontend is built with:
- Vite for bundling
- React for the UI framework
- Tailwind CSS for styling
- React Query for API state management

### Electron Configuration

The Electron app:
- Spawns the backend process on startup
- Serves the frontend from local files
- Manages process lifecycle
- Handles graceful shutdown

## File Structure

```
ipam-tool/
├── backend/
│   ├── ipam-backend.spec      # PyInstaller specification
│   ├── build_backend.py       # Backend build script
│   └── dist/                  # Backend executable output
├── frontend/
│   └── dist/                  # Frontend build output
├── electron/
│   ├── main.js               # Electron main process
│   ├── package.json          # Electron configuration
│   └── dist/                 # Final executable output
└── build-executable.py       # Complete build script
```

## Troubleshooting

### Backend Issues

- **Import errors**: Check `hiddenimports` in `ipam-backend.spec`
- **Database errors**: Ensure SQLite permissions in app data directory
- **Port conflicts**: Backend uses port 8001 by default

### Frontend Issues

- **Build failures**: Check Node.js version and dependencies
- **API connection**: Verify CORS configuration matches Electron setup
- **Asset loading**: Ensure relative paths in built files

### Electron Issues

- **Backend startup**: Check console logs for backend process errors
- **Window loading**: Verify frontend build exists and is valid
- **Packaging**: Ensure all resources are included in electron-builder config

## Distribution

The final executable will be created in `electron/dist/` and includes:
- Self-contained backend with all Python dependencies
- Complete frontend application
- SQLite database (created on first run)
- All necessary runtime files

Users can run the executable without installing Python, Node.js, or any other dependencies.

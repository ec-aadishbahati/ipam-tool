#!/usr/bin/env python3
"""
Complete build script for creating the IPAM Tool executable
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"🚀 Running: {' '.join(cmd)}")
    if cwd:
        print(f"📁 Working directory: {cwd}")
    
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"❌ Command failed with return code {result.returncode}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
    
    return result

def build_backend():
    """Build the backend executable using PyInstaller"""
    print("\n🔨 Building Backend Executable...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    build_script = backend_dir / "build_backend.py"
    result = run_command([sys.executable, str(build_script)], cwd=backend_dir)
    
    exe_name = "ipam-backend.exe" if os.name == 'nt' else "ipam-backend"
    exe_path = backend_dir / "dist" / exe_name
    
    if not exe_path.exists():
        print(f"❌ Backend executable not found at {exe_path}")
        return False
    
    print(f"✅ Backend executable created: {exe_path}")
    return True

def build_frontend():
    """Build the frontend using Vite"""
    print("\n🔨 Building Frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    print("📦 Installing frontend dependencies...")
    run_command(["npm", "install"], cwd=frontend_dir)
    
    print("🏗️ Building frontend...")
    run_command(["npm", "run", "build"], cwd=frontend_dir)
    
    dist_dir = frontend_dir / "dist"
    if not dist_dir.exists() or not (dist_dir / "index.html").exists():
        print("❌ Frontend build failed - dist/index.html not found")
        return False
    
    print(f"✅ Frontend built successfully: {dist_dir}")
    return True

def setup_electron():
    """Set up Electron packaging"""
    print("\n🔨 Setting up Electron...")
    
    electron_dir = Path(__file__).parent / "electron"
    
    print("📦 Installing Electron dependencies...")
    run_command(["npm", "install"], cwd=electron_dir)
    
    frontend_dist = Path(__file__).parent / "frontend" / "dist"
    electron_frontend = electron_dir / "frontend"
    
    if electron_frontend.exists():
        shutil.rmtree(electron_frontend)
    
    print(f"📋 Copying frontend build to Electron directory...")
    shutil.copytree(frontend_dist, electron_frontend)
    
    backend_dist = Path(__file__).parent / "backend" / "dist"
    electron_backend = electron_dir / "backend"
    
    if electron_backend.exists():
        shutil.rmtree(electron_backend)
    
    print(f"📋 Copying backend executable to Electron directory...")
    shutil.copytree(backend_dist, electron_backend)
    
    print("✅ Electron setup complete")
    return True

def build_electron():
    """Build the final Electron executable"""
    print("\n🔨 Building Electron Application...")
    
    electron_dir = Path(__file__).parent / "electron"
    
    print("🏗️ Building Electron executable...")
    run_command(["npm", "run", "build"], cwd=electron_dir)
    
    dist_dir = electron_dir / "dist"
    if not dist_dir.exists():
        print("❌ Electron build failed - dist directory not found")
        return False
    
    exe_files = list(dist_dir.glob("**/*.exe")) + list(dist_dir.glob("**/*.app")) + list(dist_dir.glob("**/*.AppImage"))
    
    if not exe_files:
        print("❌ No executable found in Electron dist directory")
        return False
    
    for exe_file in exe_files:
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"✅ Electron executable created: {exe_file} ({size_mb:.1f} MB)")
    
    return True

def main():
    """Main build process"""
    print("🚀 IPAM Tool - Complete Build Process")
    print("=====================================")
    
    root_dir = Path(__file__).parent
    print(f"📁 Root directory: {root_dir}")
    
    if not build_backend():
        print("❌ Backend build failed")
        return False
    
    if not build_frontend():
        print("❌ Frontend build failed")
        return False
    
    if not setup_electron():
        print("❌ Electron setup failed")
        return False
    
    if not build_electron():
        print("❌ Electron build failed")
        return False
    
    print("\n🎉 Build Complete!")
    print("==================")
    print("✅ Backend executable created")
    print("✅ Frontend built and packaged")
    print("✅ Electron application ready")
    print("\n📦 Find your executable in the electron/dist directory")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

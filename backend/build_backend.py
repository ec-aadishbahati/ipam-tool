#!/usr/bin/env python3
"""
Build script for creating the backend executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Build the backend executable"""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🔨 Building IPAM Backend Executable...")
    print(f"Working directory: {backend_dir}")
    
    dist_dir = backend_dir / "dist"
    build_dir = backend_dir / "build"
    
    if dist_dir.exists():
        print("🧹 Cleaning previous dist directory...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print("🧹 Cleaning previous build directory...")
        shutil.rmtree(build_dir)
    
    spec_file = backend_dir / "ipam-backend.spec"
    cmd = [sys.executable, "-m", "PyInstaller", str(spec_file)]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ PyInstaller build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    exe_path = dist_dir / "ipam-backend.exe" if os.name == 'nt' else dist_dir / "ipam-backend"
    if not exe_path.exists():
        print(f"❌ Executable not found at {exe_path}")
        return False
    
    print(f"✅ Backend executable created successfully at {exe_path}")
    print(f"📦 Executable size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

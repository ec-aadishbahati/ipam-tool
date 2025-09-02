# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(SPECPATH)
sys.path.insert(0, str(backend_dir))

block_cipher = None

# Collect all Python files from the app directory
app_files = []
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            app_files.append(os.path.join(root, file))

# Hidden imports for FastAPI and dependencies
hidden_imports = [
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.websockets',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'fastapi',
    'fastapi.routing',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'pydantic',
    'pydantic_settings',
    'sqlalchemy',
    'sqlalchemy.ext.asyncio',
    'alembic',
    'passlib',
    'passlib.hash',
    'passlib.context',
    'jose',
    'cryptography',
    'email_validator',
    'structlog',
    'openpyxl',
    'multipart',
    'python_multipart',
    'aiosqlite',
    'app.main',
    'app.core.config',
    'app.core.security',
    'app.core.startup',
    'app.db.session',
    'app.db.models',
    'app.api.routes.auth',
    'app.api.routes.purposes',
    'app.api.routes.categories',
    'app.api.routes.supernets',
    'app.api.routes.subnets',
    'app.api.routes.vlans',
    'app.api.routes.devices',
    'app.api.routes.racks',
    'app.api.routes.ip_assignments',
    'app.api.routes.audits',
    'app.api.routes.search',
    'app.api.routes.export',
    'app.api.routes.backup',
    'app.api.routes.health',
]

# Data files to include
datas = [
    ('alembic', 'alembic'),
    ('alembic.ini', '.'),
]

a = Analysis(
    ['app/main.py'],
    pathex=[backend_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ipam-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

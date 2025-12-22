# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get the absolute path to the project root
project_root = os.path.abspath(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('app/*.py', 'app'),
        ('assets/*', 'assets'),
    ],
    hiddenimports=[
        'flet',
        'flet.core',
        'flet.utils',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyo = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Check if icon exists
icon_path = 'assets/logo.ico' if os.path.exists('assets/logo.ico') else None

exe = EXE(
    pyo,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Acheiria',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

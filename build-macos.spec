# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

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
        'pynput.keyboard._darwin',
        'pynput.mouse._darwin',
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

exe = EXE(
    pyo,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Acheiria',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch='universal2',
    codesign_identity=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Acheiria',
)

# Check if icon exists, use default if not
icon_path = 'assets/logo.icns' if os.path.exists('assets/logo.icns') else None

app = BUNDLE(
    coll,
    name='Acheiria.app',
    icon=icon_path,
    bundle_identifier='com.acheiria.typingassistant',
    version='1.0.0',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleDisplayName': 'Acheiria',
        'NSHumanReadableCopyright': 'Copyright © 2024 Acheiria',
        'LSApplicationCategoryType': 'public.app-category.productivity',
    },
)

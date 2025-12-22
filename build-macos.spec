# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
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
    name='acheiria',
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
    name='acheiria',
)

app = BUNDLE(
    coll,
    name='acheiria.app',
    icon='assets/logo.icns',
    bundle_identifier='com.acheiria.typingassistant',
    version='1.0.0',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleDisplayName': 'acheiria',
        'NSHumanReadableCopyright': 'Copyright © 2024 acheiria',
        'LSApplicationCategoryType': 'public.app-category.productivity',
    },
)

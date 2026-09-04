# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

datas = [
    ('app/static', 'app/static'),
    ('assets', 'assets'),
]
if os.path.exists('alerts_data.db'):
    datas.append(('alerts_data.db', '.'))

binaries = []
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'websockets.legacy',
    'websockets.legacy.server',
    'websockets.legacy.client',
    'aiosqlite',
    'sqlite3',
]

for pkg in ['uvicorn', 'fastapi', 'starlette', 'webview', 'aiosqlite', 'pydantic', 'aiohttp']:
    try:
        pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hidden
    except Exception:
        pass

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

is_mac = sys.platform == 'darwin'
icon_path = 'assets/icon.icns' if is_mac and os.path.exists('assets/icon.icns') else ('assets/icon.ico' if os.path.exists('assets/icon.ico') else None)

if is_mac:
    # macOS: Proper onedir .app bundle
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='ukraine-alert-forecast',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='ukraine-alert-forecast',
    )

    app = BUNDLE(
        coll,
        name='UA Alert Forecast.app',
        icon=icon_path,
        bundle_identifier='com.mak74ik.ua-alert-forecast',
        info_plist={
            'CFBundleDisplayName': 'UA Alert Forecast',
            'CFBundleName': 'UA Alert Forecast',
            'CFBundleIdentifier': 'com.mak74ik.ua-alert-forecast',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '11.0.0',
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': True,
                'NSAllowsLocalNetworking': True,
            },
        }
    )
else:
    # Windows & Linux: Single executable, NO console window (console=False), UPX disabled to avoid AV false positives
    version_file = 'file_version_info.txt' if os.path.exists('file_version_info.txt') else None
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='ukraine-alert-forecast',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,
        version=version_file,
    )


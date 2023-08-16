# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

# pymorph data
import pymorphy2_dicts_ru
pymorph_data = pymorphy2_dicts_ru.get_path()

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[(pymorph_data, 'pymorphy2_dicts_ru/data'), ('ru_core_news_sm-3.6.0', 'russian_text_stresser/ru_core_news_sm-3.6.0')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)

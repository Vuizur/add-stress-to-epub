# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

# pymorph data
import pymorphy2_dicts_ru
pymorph_data = pymorphy2_dicts_ru.get_path()

a_a = Analysis(['gui.py'],
             pathex=['C:/Users/hanne/AppData/Local/pypoetry/Cache/virtualenvs/russian-text-stresser-Bfk3BIMz-py3.10'],
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
             noarchive=False)

b_a = Analysis(
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

MERGE((a_a, "gui", "gui"), (b_a, "app", "app"))

a_pyz = PYZ(a_a.pure, a_a.zipped_data,
             cipher=block_cipher)

b_pyz = PYZ(b_a.pure, b_a.zipped_data, cipher=block_cipher)
a_exe = EXE(a_pyz,
          a_a.scripts, 
          [],
          exclude_binaries=True,
          name='gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
b_exe = EXE(
    b_pyz,
    b_a.scripts,
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
a_coll = COLLECT(a_exe,
               a_a.binaries,
               a_a.zipfiles,
               a_a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='gui')

b_coll = COLLECT(
    b_exe,
    b_a.binaries,
    b_a.zipfiles,
    b_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
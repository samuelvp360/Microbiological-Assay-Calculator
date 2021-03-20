# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['MainController.py'],
             pathex=[],
             binaries=[],
             datas=[('Views/*.ui', 'Views'), ('README.md', 'README'), ('DB/*', 'DB')],
             hiddenimports=['WellProcessor', 'Models', 'DB', 'Assay', 'cmath'],
             hookspath=['.'],
             runtime_hooks=[],
             excludes=['tcl', 'tk', 'tcl8'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='svp_mac',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Microbiological_Assay_Calculator')

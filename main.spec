# -*- mode: python -*-

block_cipher = None

added_files = [
  ('assets', 'assets')
]

paths = [
  '/home/alm818/Workspace/IntroToCS/FinalProject', 
  '/home/alm818/Workspace/IntroToCS/FinalProject/scripts/ingame', 
  '/home/alm818/Workspace/IntroToCS/FinalProject/scripts/outgame', 
  '/home/alm818/Workspace/IntroToCS/FinalProject/scripts'
]

a = Analysis(['main.py'],
             pathex=paths,
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=True )

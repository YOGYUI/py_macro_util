import os
import sys
import ntpath
import pathlib
sys.setrecursionlimit(5000)

APP_NAME = 'MACRO'
block_cipher = None

a = Analysis(
    ['..\\main.py'],
    pathex=['..\\'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'logging.handlers', 'pynput', 'pywin32'
    ],
    hookspath=['.\\hook'],
    runtime_hooks=[],
    excludes=['zmq', 'PyQt5'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    strip=False,
    upx=True,
    console=False,
    # console=True,
    icon='..\\Resource\\Icon\\application.ico',
    version='.\\file_version_info.txt',
    contents_directory='.',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name=APP_NAME
)

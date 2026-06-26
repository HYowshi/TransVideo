# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


block_cipher = None

datas = [
    ("videotrans/styles", "videotrans/styles"),
    ("videotrans/language", "videotrans/language"),
    ("videotrans/prompts", "videotrans/prompts"),
    ("videotrans/voicejson", "videotrans/voicejson"),
    ("ffmpeg", "ffmpeg"),
    ("f5-tts", "f5-tts"),
    ("law.txt", "."),
]

for package in ("edge_tts", "gradio_client", "modelscope"):
    datas += collect_data_files(package)

hiddenimports = (
    collect_submodules("videotrans")
    + collect_submodules("edge_tts")
    + collect_submodules("yt_dlp")
)

a = Analysis(
    ["sp.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name="TransVideo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="videotrans/styles/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TransVideo",
)

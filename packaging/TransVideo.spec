# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from pathlib import Path


block_cipher = None
project_root = Path(SPECPATH).parent

datas = [
    (str(project_root / "videotrans" / "styles"), "videotrans/styles"),
    (str(project_root / "videotrans" / "language"), "videotrans/language"),
    (str(project_root / "videotrans" / "prompts"), "videotrans/prompts"),
    (str(project_root / "videotrans" / "voicejson"), "videotrans/voicejson"),
    (str(project_root / "ffmpeg"), "ffmpeg"),
    (str(project_root / "f5-tts"), "f5-tts"),
    (str(project_root / "law.txt"), "."),
]

for package in ("edge_tts", "gradio_client", "modelscope"):
    datas += collect_data_files(package)

hiddenimports = (
    collect_submodules("videotrans")
    + collect_submodules("edge_tts")
    + collect_submodules("yt_dlp")
)

a = Analysis(
    [str(project_root / "sp.py")],
    pathex=[str(project_root)],
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
    icon=str(project_root / "videotrans" / "styles" / "icon.ico"),
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

# PyInstaller spec: single-file exe for HF WebUI Downloader.
# Usage: pyinstaller hf_downloader.spec
# Output: dist/hf-downloader.exe

import os
from pathlib import Path

ROOT = Path(os.getcwd()).resolve()

a = Analysis(
    [str(ROOT / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[(str(ROOT / "static" / "index.html"), "static")],
    hiddenimports=[
        "huggingface_hub",
        "huggingface_hub.utils",
        "huggingface_hub.file_download",
        "huggingface_hub.hf_api",
        "huggingface_hub.utils._headers",
        "huggingface_hub.utils._cache_manager",
        "huggingface_hub.utils._http",
        "huggingface_hub.utils._login",
        "huggingface_hub.utils._paths",
        "huggingface_hub.utils._tqdm",
        "huggingface_hub.utils._download",
        "huggingface_hub.utils._errors",
        "huggingface_hub.utils._snapshot",
        "huggingface_hub.utils._repo",
        "huggingface_hub.utils._revision",
        "huggingface_hub.utils._session",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest", "setuptools", "pip", "wheel",
        "tkinter", "matplotlib", "numpy", "pandas",
        "IPython", "notebook",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="hf-downloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

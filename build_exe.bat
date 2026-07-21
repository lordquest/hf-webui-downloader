@echo off
REM Build single-file exe for HF WebUI Downloader.
REM Requirements: Python 3.9+, pip
REM Output: dist\hf-downloader.exe

echo [1/2] Installing PyInstaller (if not already installed)...
pip install -q pyinstaller

echo [2/2] Building exe via PyInstaller...
pyinstaller hf_downloader.spec

if exist "dist\hf-downloader.exe" (
    echo.
    echo Build complete: dist\hf-downloader.exe
    echo Double-click to run; browser should open automatically at http://127.0.0.1:8000
) else (
    echo Build failed; see messages above.
    pause
)

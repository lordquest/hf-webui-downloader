#!/usr/bin/env bash
# Build single-file executable for Linux using PyInstaller.
# Output: dist/hf-downloader
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1) Ensure PyInstaller is available
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[1/2] Installing PyInstaller..."
    pip3 install --user --quiet pyinstaller
else
    echo "[1/2] PyInstaller already installed."
fi

# 2) Build
echo "[2/2] Building Linux single-file executable..."
pyinstaller hf_downloader.spec

OUT="dist/hf-downloader"
if [[ -f "$OUT" ]]; then
    chmod +x "$OUT"
    echo ""
    echo "Build complete: $OUT"
    echo "Run it with: ./$OUT"
    echo "Optional port:  ./$OUT 8080"
else
    echo "Build failed; see messages above."
    exit 1
fi

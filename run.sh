#!/usr/bin/env bash
# ─── Quick launcher — aktifkan venv lalu jalankan launcher.py ────────────────
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "[ERROR] venv belum dibuat. Jalankan dulu: bash setup.sh"
    exit 1
fi

if [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"   # Windows
else
    source "$VENV_DIR/bin/activate"       # Linux / Mac
fi
python launcher.py
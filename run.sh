#!/usr/bin/env bash
# ─── Quick launcher — aktifkan venv lalu jalankan launcher.py ────────────────
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "[ERROR] venv belum dibuat. Jalankan dulu: bash setup.sh"
    exit 1
fi

source "$VENV_DIR/bin/activate"
python launcher.py
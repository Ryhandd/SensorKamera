#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  SensorKamera — Setup Script
#  Membuat virtual environment dan menginstall dependencies
# ═══════════════════════════════════════════════════════════

set -e

VENV_DIR="venv"
PYTHON="python3"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║       SensorKamera — Setup Environment       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Cek Python ──────────────────────────────────────────────
if ! command -v $PYTHON &> /dev/null; then
    echo "[ERROR] Python3 tidak ditemukan. Install dulu dengan:"
    echo "         sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo "[OK] Python: $($PYTHON --version)"

# ── Buat venv ───────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Membuat virtual environment '$VENV_DIR'..."
    $PYTHON -m venv $VENV_DIR
else
    echo "[INFO] venv '$VENV_DIR' sudah ada, dilewati."
fi

# ── Aktifkan venv ────────────────────────────────────────────
source "$VENV_DIR/bin/activate"
echo "[OK] venv aktif: $(which python)"

# ── Upgrade pip ─────────────────────────────────────────────
pip install --upgrade pip --quiet

# ── Install dependencies ──────────────────────────────────────
echo ""
echo "[INFO] Menginstall dependencies..."
echo ""

pip install \
    opencv-python \
    opencv-contrib-python \
    mediapipe \
    deepface \
    gTTS \
    pygame \
    numpy \
    tf-keras \
    --quiet

echo ""
echo "[OK] Semua dependency berhasil diinstall!"
echo ""
echo "═══════════════════════════════════════════════"
echo "  Cara menjalankan:"
echo ""
echo "    source venv/bin/activate"
echo "    python launcher.py"
echo ""
echo "  Atau langsung:"
echo "    ./run.sh"
echo "═══════════════════════════════════════════════"
echo ""
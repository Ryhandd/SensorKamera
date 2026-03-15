#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  SensorKamera — Setup Script
#  Membuat virtual environment dan menginstall dependencies
# ═══════════════════════════════════════════════════════════

set -e

VENV_DIR="venv"

# Windows pakai 'python', Linux/Mac pakai 'python3'
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "[ERROR] Python tidak ditemukan. Install dari https://python.org"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║       SensorKamera — Setup Environment       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Cek Python ──────────────────────────────────────────────
if ! command -v $PYTHON &> /dev/null; then
    echo "[ERROR] Python tidak ditemukan."
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

# ── Aktifkan venv (Windows Git Bash vs Linux/Mac) ────────────
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"   # Windows
else
    source "$VENV_DIR/bin/activate"       # Linux / Mac
fi
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
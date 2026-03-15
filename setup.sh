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
    echo "[ERROR] Python tidak ditemukan."
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║       SensorKamera — Setup Environment       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

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

# ── Upgrade pip dulu ─────────────────────────────────────────
echo "[INFO] Upgrade pip..."
python -m pip install --upgrade pip --quiet

# ── Install dependencies dengan urutan yang benar ────────────
echo ""
echo "[INFO] Menginstall dependencies (ini butuh beberapa menit)..."
echo ""

# Install numpy & keras dulu sebelum tensorflow agar tidak konflik
pip install "numpy==1.24.3" --quiet
pip install "keras==2.13.1" --quiet
pip install "typing-extensions==4.9.0" --quiet
pip install "tensorflow==2.13.0" --quiet
pip install "deepface==0.0.79" --quiet
pip install \
    opencv-python \
    opencv-contrib-python \
    "mediapipe>=0.10.0" \
    "gTTS>=2.4.0" \
    "pygame>=2.5.0" \
    --quiet

echo ""
echo "[OK] Semua dependency berhasil diinstall!"
echo ""
echo "═══════════════════════════════════════════════"
echo "  Cara menjalankan:"
echo ""
echo "    bash run.sh"
echo ""
echo "  atau manual:"
echo "    source venv/Scripts/activate  (Windows)"
echo "    source venv/bin/activate      (Linux/Mac)"
echo "    python launcher.py"
echo "═══════════════════════════════════════════════"
echo ""
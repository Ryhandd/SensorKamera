"""
Deteksi Emosi — Real-time facial emotion recognition
Menggunakan DeepFace + OpenCV
"""

import cv2
import time
import os
from deepface import DeepFace

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ─── KONFIGURASI ─────────────────────────────────────────────────────────────
SKIP_FRAMES   = 4       # Analisis DeepFace setiap N frame (hemat CPU)
SCALE_FACTOR  = 0.5     # Perkecil frame sebelum dianalisis
SMOOTH_ALPHA  = 0.3     # Smoothing emosi (EMA)

# Terjemahan emosi ke Bahasa Indonesia
EMOTION_ID = {
    "angry":     "Marah",
    "disgust":   "Jijik",
    "fear":      "Takut",
    "happy":     "Senang",
    "sad":       "Sedih",
    "surprise":  "Terkejut",
    "neutral":   "Netral",
}

# Warna per emosi (BGR)
EMOTION_COLOR = {
    "angry":    (0,   0,   220),
    "disgust":  (0,   150, 0  ),
    "fear":     (150, 0,   150),
    "happy":    (0,   220, 220),
    "sad":      (220, 100, 0  ),
    "surprise": (0,   200, 255),
    "neutral":  (180, 180, 180),
}
DEFAULT_COLOR = (0, 255, 0)

# ─── INIT ─────────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

frame_idx    = 0
last_results = []          # Simpan hasil deteksi terakhir
fps_prev     = time.time()
fps_display  = 0.0

UI_BG  = (15, 15, 15)
UI_DIM = (100, 100, 100)

print("[INFO] Deteksi emosi aktif — tekan Q untuk keluar.")

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Kamera tidak bisa dibaca.")
        break

    h, w = frame.shape[:2]

    # ── Analisis (tidak setiap frame agar ringan) ────────────────────────────
    if frame_idx % SKIP_FRAMES == 0:
        small = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
        try:
            last_results = DeepFace.analyze(
                small,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
        except Exception:
            last_results = []

    # ── Render kotak & label ─────────────────────────────────────────────────
    for res in last_results:
        # Kembalikan koordinat ke ukuran asli
        inv = 1.0 / SCALE_FACTOR
        rx = int(res["region"]["x"] * inv)
        ry = int(res["region"]["y"] * inv)
        rw = int(res["region"]["w"] * inv)
        rh = int(res["region"]["h"] * inv)

        emotion_raw = res.get("dominant_emotion", "neutral")
        emotion_id  = EMOTION_ID.get(emotion_raw, emotion_raw.capitalize())
        color       = EMOTION_COLOR.get(emotion_raw, DEFAULT_COLOR)

        # Kotak wajah
        cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), color, 2)

        # Label background
        (tw, th), _ = cv2.getTextSize(
            f"  {emotion_id}  ", cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
        cv2.rectangle(frame,
                      (rx, ry - th - 14),
                      (rx + tw, ry),
                      color, -1)
        cv2.putText(frame, emotion_id,
                    (rx + 6, ry - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

        # Emotion bar chart (semua emosi)
        scores = res.get("emotion", {})
        if scores:
            bar_x  = rx + rw + 10
            bar_y0 = ry
            bar_h  = max(14, rh // 8)
            for idx, (em, score) in enumerate(sorted(
                    scores.items(), key=lambda kv: -kv[1])):
                label_id = EMOTION_ID.get(em, em[:3])
                blen     = int(score * 1.2)  # maks ~120 px untuk 100%
                bcolor   = EMOTION_COLOR.get(em, DEFAULT_COLOR)
                by       = bar_y0 + idx * (bar_h + 4)
                if bar_x + 130 < w and by + bar_h < h:
                    cv2.rectangle(frame,
                                  (bar_x, by),
                                  (bar_x + max(blen, 3), by + bar_h),
                                  bcolor, -1)
                    cv2.putText(frame,
                                f"{label_id[:6]} {score:.0f}%",
                                (bar_x + max(blen, 3) + 4, by + bar_h - 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.38,
                                (200, 200, 200), 1)

    # ── FPS counter ──────────────────────────────────────────────────────────
    now = time.time()
    fps_display = 0.9 * fps_display + 0.1 * (1.0 / max(now - fps_prev, 1e-6))
    fps_prev    = now

    # ── Header & Footer ───────────────────────────────────────────────────────
    cv2.rectangle(frame, (0, 0), (w, 40), UI_BG, -1)
    cv2.putText(frame, "Deteksi Emosi — DeepFace",
                (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 150), 2)
    cv2.putText(frame, f"FPS: {fps_display:.0f}",
                (w - 100, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, UI_DIM, 1)

    cv2.rectangle(frame, (0, h - 30), (w, h), UI_BG, -1)
    cv2.putText(frame, "Q = Keluar",
                (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, UI_DIM, 1)

    frame_idx += 1
    cv2.imshow("Deteksi Emosi — SensorKamera", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
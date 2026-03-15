"""
Tambah Wajah — Daftarkan wajah baru ke dataset
"""

import cv2
import os
import sys

# ─── KONFIGURASI ─────────────────────────────────────────────────────────────
DATASET_DIR  = "dataset"
JUMLAH_FOTO  = 40       # Jumlah sampel per pengguna
UI_BG        = (15, 15, 15)
UI_DIM       = (100, 100, 100)
COLOR_OK     = (0, 255, 150)
COLOR_WARN   = (0, 200, 255)

# ─── PERSIAPAN ────────────────────────────────────────────────────────────────
os.makedirs(DATASET_DIR, exist_ok=True)

print("\n╔══════════════════════════════╗")
print("║   Pendaftaran Wajah Baru     ║")
print("╚══════════════════════════════╝\n")

nama_user = input("  Masukkan nama Anda : ").strip()
if not nama_user:
    print("[ERROR] Nama tidak boleh kosong.")
    sys.exit(1)

nama_folder = nama_user.lower().replace(" ", "_")
path_user   = os.path.join(DATASET_DIR, nama_folder)
os.makedirs(path_user, exist_ok=True)

# Hitung foto yang sudah ada agar tidak overwrite
existing   = [f for f in os.listdir(path_user) if f.endswith(".jpg")]
start_idx  = len(existing) + 1
print(f"\n  Halo, {nama_user}! Akan mengambil {JUMLAH_FOTO} foto.")
if existing:
    print(f"  ({len(existing)} foto lama tetap disimpan, mulai dari index {start_idx})")

# ─── KAMERA & DETEKTOR ───────────────────────────────────────────────────────
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
if not os.path.exists(cascade_path):
    print(f"[ERROR] Haar cascade tidak ditemukan: {cascade_path}")
    cam.release()
    sys.exit(1)

face_det = cv2.CascadeClassifier(cascade_path)
count    = 0

print("\n  [INFO] Posisikan wajah di dalam kotak. Jangan bergerak terlalu cepat.")
print("  [INFO] Tekan ESC untuk batal.\n")

# ─── LOOP ────────────────────────────────────────────────────────────────────
while True:
    ret, frame = cam.read()
    if not ret:
        print("[ERROR] Gagal membaca kamera.")
        break

    frame  = cv2.flip(frame, 1)
    h, w   = frame.shape[:2]
    gray   = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces  = face_det.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5,
                                       minSize=(80, 80))

    for (x, y, fw, fh) in faces:
        if count < JUMLAH_FOTO:
            idx      = start_idx + count
            fname    = os.path.join(path_user, f"{nama_folder}_{idx}.jpg")
            roi_gray = gray[y:y+fh, x:x+fw]
            cv2.imwrite(fname, roi_gray)
            count += 1

        # Visualisasi
        progress = count / JUMLAH_FOTO
        bar_len  = int(progress * 200)
        color    = COLOR_OK if count < JUMLAH_FOTO else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)

    # ── Header ───────────────────────────────────────────────────────────────
    cv2.rectangle(frame, (0, 0), (w, 55), UI_BG, -1)
    cv2.putText(frame, f"Mendaftarkan: {nama_user}",
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WARN, 1)

    # Progress bar
    total     = JUMLAH_FOTO
    bar_x0, bar_y0 = 10, 30
    bar_full  = w - 20
    bar_done  = int((count / total) * bar_full)
    cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x0 + bar_full, bar_y0 + 14),
                  (40, 40, 40), -1)
    cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x0 + bar_done, bar_y0 + 14),
                  COLOR_OK, -1)
    cv2.putText(frame, f"{count}/{total} foto",
                (bar_x0 + bar_full + 6, bar_y0 + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, UI_DIM, 1)

    # ── Footer ────────────────────────────────────────────────────────────────
    cv2.rectangle(frame, (0, h - 30), (w, h), UI_BG, -1)
    cv2.putText(frame, "ESC = Batal",
                (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, UI_DIM, 1)

    cv2.imshow("Pendaftaran Wajah — SensorKamera", frame)

    key = cv2.waitKey(30) & 0xFF
    if key == 27:
        print(f"\n[INFO] Dibatalkan. {count} foto tersimpan.")
        break
    if count >= JUMLAH_FOTO:
        print(f"\n[INFO] {count} sampel berhasil diambil untuk '{nama_user}'.")
        break

cam.release()
cv2.destroyAllWindows()
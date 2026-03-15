"""
Kenali Wajah — Face recognition dari dataset lokal
Menggunakan LBPH Face Recognizer (OpenCV)
"""

import cv2
import os
import sys
import numpy as np

# ─── KONFIGURASI ─────────────────────────────────────────────────────────────
DATASET_PATH    = "dataset"
CONFIDENCE_THRESH = 78      # < nilai ini = dikenal (LBPH: makin kecil makin baik)
UI_BG           = (15, 15, 15)
UI_DIM          = (100, 100, 100)
COLOR_KNOWN     = (0,  255, 150)
COLOR_UNKNOWN   = (0,  60,  220)

# ─── CEK DATASET ─────────────────────────────────────────────────────────────
if not os.path.exists(DATASET_PATH):
    print(f"[ERROR] Folder dataset '{DATASET_PATH}' tidak ditemukan.")
    print("         Jalankan 'Tambah Wajah' terlebih dahulu.")
    sys.exit(1)

# ─── TRAINING ────────────────────────────────────────────────────────────────
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)
recognizer   = cv2.face.LBPHFaceRecognizer_create()

faces, ids, names = [], [], ["Tidak Dikenal"]  # index 0 = unknown
current_id = 1
skipped    = 0

print("[INFO] Melatih model wajah...", end=" ", flush=True)

for person_name in sorted(os.listdir(DATASET_PATH)):
    person_path = os.path.join(DATASET_PATH, person_name)
    if not os.path.isdir(person_path):
        continue

    label_display = person_name.replace("_", " ").title()
    person_faces  = 0

    for filename in os.listdir(person_path):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        img_path = os.path.join(person_path, filename)
        img      = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            skipped += 1
            continue
        # Resize agar konsisten dengan ukuran yang disimpan add_face.py
        img = cv2.resize(img, (200, 200))
        faces.append(img)
        ids.append(current_id)
        person_faces += 1

    if person_faces > 0:
        names.append(label_display)
        print(f"\n  [{current_id}] {label_display} — {person_faces} foto", end="")
        current_id += 1

if not faces:
    print("\n[ERROR] Tidak ada gambar valid di dataset.")
    sys.exit(1)

recognizer.train(faces, np.array(ids))
print(f"\n\n[INFO] {current_id-1} wajah dimuat ({skipped} file dilewati). Membuka kamera...")

# ─── KAMERA ──────────────────────────────────────────────────────────────────
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

import time
fps_prev    = time.time()
fps_display = 0.0

# ─── LOOP ────────────────────────────────────────────────────────────────────
while True:
    ret, frame = cam.read()
    if not ret:
        break

    frame  = cv2.flip(frame, 1)
    h, w   = frame.shape[:2]
    gray   = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    detected = face_cascade.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

    for (x, y, fw, fh) in detected:
        roi    = cv2.resize(gray[y:y+fh, x:x+fw], (200, 200))
        pid, conf = recognizer.predict(roi)

        # Confidence LBPH: 0=sempurna, makin besar makin buruk
        is_known = conf < CONFIDENCE_THRESH
        name     = names[pid] if is_known else "Tidak Dikenal"
        pct      = max(0, round(100 - conf))
        color    = COLOR_KNOWN if is_known else COLOR_UNKNOWN

        # Kotak wajah
        cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)

        # Label
        label = f"{name}  {pct}%" if is_known else name
        (tw, th), _ = cv2.getTextSize(
            f"  {label}  ", cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
        cv2.rectangle(frame,
                      (x, y - th - 14), (x + tw, y),
                      color, -1)
        cv2.putText(frame, label,
                    (x + 6, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)

    # ── FPS ──────────────────────────────────────────────────────────────────
    now = time.time()
    fps_display = 0.9 * fps_display + 0.1 / max(now - fps_prev, 1e-6)
    fps_prev    = now

    # ── Header & Footer ───────────────────────────────────────────────────────
    cv2.rectangle(frame, (0, 0), (w, 40), UI_BG, -1)
    cv2.putText(frame, f"Pengenalan Wajah  [{current_id-1} orang]",
                (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 150), 2)
    cv2.putText(frame, f"FPS: {fps_display:.0f}",
                (w - 100, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, UI_DIM, 1)

    cv2.rectangle(frame, (0, h - 30), (w, h), UI_BG, -1)
    cv2.putText(frame, "Q = Keluar",
                (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, UI_DIM, 1)

    cv2.imshow("Kenali Wajah — SensorKamera", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()
import cv2
from deepface import DeepFace
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

cap = cv2.VideoCapture(0)

# Variabel untuk optimasi
frame_count = 0
skip_frames = 5  # Hanya deteksi emosi setiap 5 frame sekali
results = []     # Simpan hasil deteksi terakhir

print("[INFO] Deteksi emosi ringan dimulai...")

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. OPTIMASI: Perkecil ukuran frame yang akan dianalisa (misal: 1/2 ukuran asli)
    # Ini bikin proses AI jauh lebih cepat
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # 2. OPTIMASI: Frame Skipping
    # Kita nggak perlu deteksi emosi di SETIAP frame (boros CPU)
    if frame_count % skip_frames == 0:
        try:
            # Analisa pakai frame yang sudah diperkecil
            results = DeepFace.analyze(small_frame, actions=['emotion'], enforce_detection=False)
        except Exception as e:
            pass

    # Tampilkan hasil deteksi terakhir ke frame asli
    for res in results:
        # Kembalikan koordinat kotak ke ukuran asli (karena tadi dikecilin 0.5x, maka dikali 2)
        x, y, w, h = [v * 2 for v in [res['region']['x'], res['region']['y'], res['region']['w'], res['region']['h']]]
        
        emotion = res['dominant_emotion']
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"Emosi: {emotion}", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    frame_count += 1

    # Tampilan Quit tetap di luar agar selalu muncul
    cv2.rectangle(frame, (0, frame.shape[0]-35), (220, frame.shape[0]), (0,0,0), -1)
    cv2.putText(frame, "Press 'Q' to Quit", (10, frame.shape[0]-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow('Deteksi Emosi Ringan', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
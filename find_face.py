import cv2
import os
import numpy as np

# --- PENGATURAN ---
dataset_path = "dataset"
# ------------------

# Inisialisasi Detektor Wajah & Recognizer
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

# List untuk data training
faces = []
ids = []
names = ['Tidak Dikenal'] # Index 0

print("[INFO] Melatih data wajah... Tunggu sebentar.")

# Proses semua folder di dataset
current_id = 1
for name in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, name)
    if os.path.isdir(person_path):
        names.append(name.replace("_", " ").title())
        for filename in os.listdir(person_path):
            img_path = os.path.join(person_path, filename)
            gray_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if gray_img is not None:
                faces.append(gray_img)
                ids.append(current_id)
        current_id += 1

# Training model
recognizer.train(faces, np.array(ids))
print(f"[INFO] {len(names)-1} Wajah berhasil dimuat. Membuka kamera...")

# Jalankan Kamera
cam = cv2.VideoCapture(0)

while True:
    ret, frame = cam.read()
    if not ret: break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in detected_faces:
        id_pred, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        
        # Confidence di LBPH: semakin kecil angka, semakin mirip (0 = sempurna)
        if confidence < 80:
            name = names[id_pred]
            label = f"{name} ({round(100 - confidence)}%)"
            color = (0, 255, 0) # Hijau
        else:
            name = "Tidak Dikenal"
            label = name
            color = (0, 0, 255) # Merah

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # --- TAMBAHAN OVERLAY QUIT ---
    cv2.rectangle(frame, (0, frame.shape[0]-35), (220, frame.shape[0]), (0,0,0), -1)
    cv2.putText(frame, "Press 'Q' to Quit", (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow('Face Recognition - OpenCV Mode', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
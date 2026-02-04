import cv2
import os

# --- PENGATURAN ---
nama_folder_dataset = "dataset"
jumlah_sampel = 30 # Jumlah foto sampel yang akan diambil
# ------------------

# Pastikan folder dataset ada
if not os.path.exists(nama_folder_dataset):
    os.makedirs(nama_folder_dataset)
    print(f"Folder '{nama_folder_dataset}' berhasil dibuat.")

# Minta input nama pengguna
nama_user = input("Masukkan nama Anda: ").lower().replace(" ", "_")
path_user = os.path.join(nama_folder_dataset, nama_user)

# Buat folder khusus untuk user jika belum ada
if not os.path.exists(path_user):
    os.makedirs(path_user)
    print(f"Folder untuk '{nama_user}' berhasil dibuat.")
else:
    print(f"Folder untuk '{nama_user}' sudah ada. Menambahkan gambar baru...")

# Inisialisasi kamera
cam = cv2.VideoCapture(0)
cam.set(3, 640) # Lebar frame
cam.set(4, 480) # Tinggi frame

# Gunakan detektor wajah bawaan OpenCV (Haar Cascade)
# Pastikan file haarcascade_frontalface_default.xml ada di folder yang sama
# atau berikan path lengkapnya.
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("\n[INFO] Menyalakan kamera. Posisikan wajah Anda di depan kamera dan jangan bergerak...")
count = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("[ERROR] Gagal mengambil gambar dari kamera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        count += 1

        # Simpan gambar wajah yang terdeteksi
        nama_file = os.path.join(path_user, f"{nama_user}_{count}.jpg")
        cv2.imwrite(nama_file, gray[y:y+h, x:x+w])

        # Tampilkan frame di jendela
        cv2.imshow('Pendaftaran Wajah', frame)

    # Cek tombol 'ESC' untuk keluar atau jika sampel sudah cukup
    k = cv2.waitKey(100) & 0xff
    if k == 27: # 27 adalah kode ASCII untuk tombol ESC
        break
    elif count >= jumlah_sampel:
        break

# Cleanup
print(f"\n[INFO] {count} sampel wajah berhasil diambil. Menutup program.")
cam.release()
cv2.destroyAllWindows()
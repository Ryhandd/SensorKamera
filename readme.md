# 📷 SensorKamera

Kumpulan tools Computer Vision berbasis Python untuk:
- 🤟 Deteksi Bahasa Isyarat Indonesia (SIBI) — huruf A–Z
- 😄 Deteksi Emosi wajah real-time (DeepFace)
- 👤 Pendaftaran & Pengenalan Wajah (OpenCV LBPH)
- ✊ Deteksi gestur khusus (Jokowi)

---

## 🚀 Cara Mulai

### 🪟 Windows (CMD — Direkomendasikan)

> Buka **CMD as Administrator** (klik kanan ikon CMD → Run as administrator)

```cmd
cd D:\path\ke\SensorKamera
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Setelah install selesai, untuk menjalankan berikutnya cukup:
```cmd
venv\Scripts\activate
python launcher.py
```

---

### 🐚 Windows — Git Bash

Kalau ingin tetap pakai Git Bash, **install dulu lewat CMD Administrator** (langkah di atas), lalu jalankan via Git Bash:
```bash
source venv/Scripts/activate
python launcher.py
```

> ⚠️ Jangan install packages dari Git Bash di Windows — rawan `[WinError 5] Access Denied`.
> Gunakan CMD Administrator untuk proses install.

---

### 🐧 Linux / Mac

```bash
# Setup (sekali saja)
bash setup.sh

# Jalankan
bash run.sh
```

atau manual:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python launcher.py
```

---

## 📁 Struktur File

```
SensorKamera/
├── launcher.py        ← Menu utama (jalankan ini)
├── sibi.py            ← SIBI Reader A–Z
├── emotion.py         ← Deteksi emosi
├── add_face.py        ← Daftar wajah baru
├── find_face.py       ← Kenali wajah
├── jokowi.py          ← Mode gestur khusus
├── dataset/           ← Otomatis dibuat saat add_face
├── setup.sh           ← Setup venv (Linux/Mac)
├── run.sh             ← Quick launcher (Linux/Mac)
└── requirements.txt
```

---

## 🤟 Panduan Gestur SIBI

| Huruf | Gestur |
|-------|--------|
| A | Kepalan, jempol di samping (naik) |
| B | 4 jari tegak, jempol melipat ke dalam |
| C | Tangan setengah melengkung (busur C) |
| D | Telunjuk tegak, jempol menyentuh jari tengah |
| E | Kepalan, jempol di depan |
| F | Jempol + telunjuk membentuk lingkaran, 3 jari lain tegak |
| G | Telunjuk horizontal ke samping |
| H | Telunjuk + tengah horizontal berdampingan |
| I | Hanya kelingking tegak |
| J | Kelingking tegak + miring |
| K | Telunjuk + tengah tegak, jempol di antara |
| L | Jempol + telunjuk membentuk huruf L |
| M | Kepalan, jempol di bawah 3 jari |
| N | Kepalan, jempol di sela telunjuk-tengah |
| O | Semua jari + jempol membentuk O |
| P | Seperti K, arah ke bawah |
| Q | Seperti G, arah ke bawah |
| R | Telunjuk + tengah bersilang |
| S | Kepalan, jempol di depan jari |
| T | Jempol naik melewati sendi telunjuk |
| U | Telunjuk + tengah tegak rapat |
| V | Telunjuk + tengah tegak terbuka (Victory) |
| W | Telunjuk + tengah + manis tegak |
| X | Telunjuk bengkok/hook |
| Y | Jempol + kelingking (Shaka) |
| Z | Telunjuk tegak, miring ke kanan |

---

## ⚙️ Catatan

- Pastikan kamera terhubung dan tidak dipakai aplikasi lain
- Tekan **Q** untuk keluar dari mode manapun
- Dataset wajah tersimpan di folder `dataset/`
- Untuk pengenalan wajah: daftarkan minimal 30 foto per orang
- Python yang didukung: **3.8 – 3.11** (Python 3.12+ belum stabil untuk MediaPipe)
# 📷 SensorKamera

Kumpulan tools Computer Vision berbasis Python untuk:
- 🤟 Deteksi Bahasa Isyarat Indonesia (SIBI) — huruf A–Z
- 😊 Deteksi Emosi wajah real-time (DeepFace)
- 👤 Pendaftaran & Pengenalan Wajah (OpenCV LBPH)
- ✊ Deteksi gestur khusus (Mode Jokowi)

---

## 🚀 Cara Mulai

### 1. Setup (sekali saja)
```bash
bash setup.sh
```
Script ini akan:
- Membuat virtual environment `venv/`
- Menginstall semua dependency otomatis

### 2. Jalankan
```bash
bash run.sh
```
atau manual:
```bash
source venv/bin/activate
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
├── setup.sh           ← Setup venv + install
├── run.sh             ← Quick launcher
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
"""
SIBI Reader — Sistem Isyarat Bahasa Indonesia
Deteksi huruf A–Z menggunakan MediaPipe Hands + gTTS
"""

import os
import cv2
import time
import math
import threading
import mediapipe as mp
from gtts import gTTS
from pygame import mixer

# ─── SETUP ──────────────────────────────────────────────────────────────────
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)

mixer.init()

# ─── AUDIO ──────────────────────────────────────────────────────────────────
def speak(text: str):
    def _run():
        fname = f"sibi_{int(time.time()*1000)}.mp3"
        try:
            gTTS(text=text, lang="id").save(fname)
            mixer.music.load(fname)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.05)
            mixer.music.unload()
        except Exception:
            pass
        finally:
            if os.path.exists(fname):
                try: os.remove(fname)
                except: pass
    threading.Thread(target=_run, daemon=True).start()

def cleanup_mp3():
    for f in os.listdir("."):
        if f.startswith("sibi_") and f.endswith(".mp3"):
            try: os.remove(f)
            except: pass

# ─── LANDMARK HELPERS ───────────────────────────────────────────────────────
def dist(lm, i, j) -> float:
    return math.hypot(lm[i].x - lm[j].x, lm[i].y - lm[j].y)

def finger_up(lm, tip, pip) -> bool:
    """Jari dianggap tegak jika ujung (tip) lebih tinggi dari sendi tengah (pip)."""
    return lm[tip].y < lm[pip].y

def finger_curled(lm, tip, mcp) -> bool:
    """Jari melipat: ujung lebih rendah dari mcp."""
    return lm[tip].y > lm[mcp].y

def thumb_open(lm, palm_size) -> bool:
    return dist(lm, 4, 17) > palm_size * 1.05

def all_closed(lm) -> bool:
    return (not finger_up(lm, 8, 6) and not finger_up(lm, 12, 10)
            and not finger_up(lm, 16, 14) and not finger_up(lm, 20, 18))

# ─── SINGLE-HAND GESTURE RECOGNITION ────────────────────────────────────────
def detect_single(lm) -> str:
    """
    Kembalikan huruf yang terdeteksi (string) atau "" kalau tidak ada.
    Landmark indices:
      Thumb : 1-2-3-4      Index  : 5-6-7-8
      Middle: 9-10-11-12   Ring   : 13-14-15-16
      Pinky : 17-18-19-20  Wrist  : 0
    """
    palm = dist(lm, 0, 9)
    if palm < 1e-6:
        return ""

    # Status tiap jari (True = tegak / terbuka)
    t  = thumb_open(lm, palm)          # Jempol
    i  = finger_up(lm, 8,  6)          # Telunjuk
    m  = finger_up(lm, 12, 10)         # Tengah
    r  = finger_up(lm, 16, 14)         # Manis
    p  = finger_up(lm, 20, 18)         # Kelingking

    # Posisi relatif tips
    d48  = dist(lm, 4, 8)   # Jempol – Telunjuk tip
    d412 = dist(lm, 4, 12)  # Jempol – Tengah tip
    d416 = dist(lm, 4, 16)
    d420 = dist(lm, 4, 20)
    d812 = dist(lm, 8, 12)  # Telunjuk – Tengah tip

    # ── H (Prioritas: Telunjuk & Tengah horizontal, saling dekat) ──────────
    x8_dist  = abs(lm[8].x - lm[5].x)
    y8_dist  = abs(lm[8].y - lm[5].y)
    x12_dist = abs(lm[12].x - lm[9].x)
    y12_dist = abs(lm[12].y - lm[9].y)
    if (x8_dist > y8_dist and x12_dist > y12_dist
            and x8_dist > palm * 0.65 and not r and not p):
        return "H"

    # ── A  (Kepalan, jempol di samping telunjuk, tegak ke atas) ─────────────
    if not i and not m and not r and not p and not t:
        # Jempol naik ke samping atau sedikit di atas kepalan
        if lm[4].y < lm[5].y or lm[4].x > lm[5].x:
            return "A"

    # ── B  (4 jari tegak, jempol ke dalam) ──────────────────────────────────
    if i and m and r and p and not t:
        return "B"

    # ── C  (Jari semi-melengkung, tangan membentuk busur) ───────────────────
    if not i and not m and not r and not p:
        # Telunjuk melipat setengah: tip lebih rendah dari pip tapi lebih tinggi dari mcp
        c_shape = (lm[8].y > lm[6].y and lm[8].y < lm[5].y
                   and lm[12].y > lm[10].y and lm[12].y < lm[9].y)
        if c_shape and t:
            return "C"

    # ── D  (Telunjuk tegak, jari lain melipat, ujung tengah-jempol menyentuh) ─
    if i and not m and not r and not p:
        if d412 < palm * 0.45:
            return "D"

    # ── E  (Semua jari mengepal, jempol di depan) ───────────────────────────
    if not i and not m and not r and not p and not t:
        if lm[4].x < lm[5].x:
            return "E"

    # ── F  (Telunjuk + Jempol membentuk lingkaran, jari lain tegak) ─────────
    if not i and m and r and p:
        if d48 < palm * 0.4:
            return "F"

    # ── G  (Telunjuk horizontal ke samping, jempol sejajar) ─────────────────
    if i and not m and not r and not p:
        if abs(lm[8].x - lm[5].x) > abs(lm[8].y - lm[5].y):
            return "G"

    # ── I  (Hanya kelingking tegak) ─────────────────────────────────────────
    if not i and not m and not r and p and not t:
        return "I"

    # ── J  (Kelingking tegak + gerakan — kita pakai proxy: kelingking + jempol) ─
    if not i and not m and not r and p and t:
        if lm[20].x < lm[18].x:  # Kelingking miring ke kiri
            return "J"

    # ── K  (Telunjuk & Tengah tegak, jempol di antara mereka) ───────────────
    if i and m and not r and not p and t:
        # Jempol diapit telunjuk dan tengah (secara X)
        tx = lm[4].x
        if min(lm[8].x, lm[12].x) < tx < max(lm[8].x, lm[12].x):
            return "K"

    # ── L  (Jempol + Telunjuk membentuk L) ──────────────────────────────────
    if t and i and not m and not r and not p:
        return "L"

    # ── M  (3 jari di atas jempol yang terlipat) ────────────────────────────
    if not i and not m and not r and not p and not t:
        # Jempol masuk di bawah 3 jari
        if (lm[4].x > lm[6].x and lm[4].x > lm[10].x
                and lm[4].x > lm[14].x):
            return "M"

    # ── N  (Seperti M tapi hanya 2 jari) ────────────────────────────────────
    if not i and not m and not r and not p and not t:
        if lm[5].x < lm[4].x < lm[9].x:
            return "N"

    # ── O  (Semua ujung menyentuh jempol membentuk O) ───────────────────────
    if not i and not m and not r and not p:
        if d48 < palm * 0.4 and d412 < palm * 0.55:
            return "O"

    # ── P  (Seperti K tapi mengarah ke bawah) ───────────────────────────────
    if i and m and not r and not p and t:
        if lm[8].y > lm[5].y:  # Telunjuk mengarah ke bawah
            return "P"

    # ── Q  (Seperti G tapi mengarah ke bawah) ───────────────────────────────
    if i and not m and not r and not p and t:
        if lm[8].y > lm[5].y:
            return "Q"

    # ── R  (Telunjuk & Tengah bersilang / berdekatan) ───────────────────────
    if i and m and not r and not p:
        if d812 < palm * 0.12:
            return "R"

    # ── S  (Kepalan, jempol di depan jari) ──────────────────────────────────
    if not i and not m and not r and not p and not t:
        if lm[4].y < lm[8].y and lm[4].x < lm[9].x:
            return "S"

    # ── T  (Jempol di antara telunjuk & tengah, telunjuk melipat) ───────────
    if not i and not m and not r and not p and not t:
        if lm[4].y < lm[6].y:  # Jempol naik melewati sendi telunjuk
            return "T"

    # ── U  (Telunjuk & Tengah tegak rapat) ──────────────────────────────────
    if i and m and not r and not p:
        if d812 < palm * 0.18:
            return "U"

    # ── V  (Telunjuk & Tengah tegak, terbuka / Victory) ─────────────────────
    if i and m and not r and not p:
        if d812 > palm * 0.18:
            return "V"

    # ── W  (Telunjuk, Tengah, Manis tegak) ──────────────────────────────────
    if i and m and r and not p:
        return "W"

    # ── X  (Telunjuk bengkok / hook) ────────────────────────────────────────
    if not i and not m and not r and not p:
        # Telunjuk: tip lebih rendah dari pip, tapi pip lebih tinggi dari mcp
        if lm[8].y > lm[7].y and lm[7].y < lm[6].y:
            return "X"

    # ── Y  (Jempol + Kelingking terbuka — "Shaka") ──────────────────────────
    if t and not i and not m and not r and p:
        return "Y"

    # ── Z  (Telunjuk tegak, gerakan zigzag — proxy: miring ke kanan) ────────
    if i and not m and not r and not p and not t:
        if lm[8].x > lm[6].x + palm * 0.15:  # Miring ke kanan
            return "Z"

    # ── Nama (fallback SIBI dua tangan) ─────────────────────────────────────
    return ""


# ─── TWO-HAND: NAMA ──────────────────────────────────────────────────────────
def detect_two_hands(lm1, lm2) -> str:
    def _pointing(lm): return lm[8].y < lm[6].y

    pointer, base = None, None
    if _pointing(lm1): pointer, base = lm1, lm2
    elif _pointing(lm2): pointer, base = lm2, lm1

    if pointer is None:
        return ""
    d = abs(pointer[8].x - base[5].x) + abs(pointer[8].y - base[8].y)
    return "Nama" if d < 0.45 else ""


# ─── INIT ────────────────────────────────────────────────────────────────────
cleanup_mp3()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

last_gesture    = ""
last_speak_time = 0
SPEAK_COOLDOWN  = 2.0       # detik
STABLE_FRAMES   = 6
TWO_HAND_FRAMES = 6

gesture_counter   = {}
stable_gesture    = ""
two_hand_counter  = 0

# Warna UI
UI_BG   = (15, 15, 15)
UI_TEXT = (0, 255, 180)
UI_DIM  = (100, 100, 100)

print("[SIBI] SIBI Reader aktif — tekan Q untuk keluar.")

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame  = cv2.flip(frame, 1)
    h, w   = frame.shape[:2]
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    detected = ""

    if result.multi_hand_landmarks:
        n = len(result.multi_hand_landmarks)

        if n >= 2:
            # Gambar kedua tangan
            for hl in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
            lm1 = result.multi_hand_landmarks[0].landmark
            lm2 = result.multi_hand_landmarks[1].landmark
            two_hand_res = detect_two_hands(lm1, lm2)
            if two_hand_res:
                two_hand_counter += 1
                if two_hand_counter >= TWO_HAND_FRAMES:
                    detected = two_hand_res
            else:
                two_hand_counter = 0
        else:
            two_hand_counter = 0

        if n == 1 and detected == "":
            hl = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
            detected = detect_single(hl.landmark)

    # ── Stabilizer ──────────────────────────────────────────────────────────
    if detected:
        gesture_counter[detected] = gesture_counter.get(detected, 0) + 1
        if gesture_counter[detected] >= STABLE_FRAMES:
            stable_gesture = detected
    else:
        gesture_counter.clear()
        stable_gesture = ""

    # ── Speak ────────────────────────────────────────────────────────────────
    now = time.time()
    if (stable_gesture
            and stable_gesture != last_gesture
            and now - last_speak_time > SPEAK_COOLDOWN):
        speak(stable_gesture)
        last_gesture    = stable_gesture
        last_speak_time = now

    # ── UI ───────────────────────────────────────────────────────────────────
    # Header bar
    cv2.rectangle(frame, (0, 0), (w, 60), UI_BG, -1)
    cv2.putText(frame, "SIBI Reader",
                (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, UI_DIM, 1)

    # Huruf terdeteksi (besar)
    label = stable_gesture if stable_gesture else "—"
    cv2.putText(frame, label,
                (12, 56), cv2.FONT_HERSHEY_SIMPLEX, 1.4, UI_TEXT, 3)

    # Indikator confidence bar
    conf  = min(gesture_counter.get(stable_gesture, 0), STABLE_FRAMES)
    bar_w = int((conf / STABLE_FRAMES) * 200)
    cv2.rectangle(frame, (w - 220, 15), (w - 20, 35), (40, 40, 40), -1)
    cv2.rectangle(frame, (w - 220, 15), (w - 220 + bar_w, 35), UI_TEXT, -1)
    cv2.putText(frame, "Confidence",
                (w - 220, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, UI_DIM, 1)

    # Footer
    cv2.rectangle(frame, (0, h - 30), (w, h), UI_BG, -1)
    cv2.putText(frame, "Q = Keluar",
                (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, UI_DIM, 1)

    cv2.imshow("SIBI Reader — Bahasa Isyarat Indonesia", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
cleanup_mp3()
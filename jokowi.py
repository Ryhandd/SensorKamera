"""
Mode Jokowi — Deteksi gestur Selamat / Berjuang / Sukses
"""

import os
import cv2
import time
import math
import threading
import mediapipe as mp
from gtts import gTTS
from pygame import mixer

# ─── SETUP ───────────────────────────────────────────────────────────────────
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8,
)

mixer.init()

# ─── AUDIO ───────────────────────────────────────────────────────────────────
def speak(text: str):
    def _run():
        fname = f"jk_{int(time.time()*1000)}.mp3"
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
        if f.startswith("jk_") and f.endswith(".mp3"):
            try: os.remove(f)
            except: pass

def dist(lm, i, j) -> float:
    return math.hypot(lm[i].x - lm[j].x, lm[i].y - lm[j].y)

# ─── GESTURE CONFIG ───────────────────────────────────────────────────────────
# Warna & label untuk setiap gestur
GESTURE_STYLE = {
    "Sukses":   {"color": (0, 220, 80),  "icon": "👍"},
    "Berjuang": {"color": (0, 160, 255), "icon": "✊"},
    "Selamat":  {"color": (255, 200, 0), "icon": "🤟"},
}

# ─── INIT ─────────────────────────────────────────────────────────────────────
cleanup_mp3()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

last_gesture    = ""
last_speak_time = 0
SPEAK_COOLDOWN  = 2.5
STABLE_FRAMES   = 6
gesture_counter = {}
stable_gesture  = ""

UI_BG  = (15, 15, 15)
UI_DIM = (100, 100, 100)

print("[INFO] Mode Jokowi aktif — tekan Q untuk keluar.")

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
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
        hand = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        lm   = hand.landmark
        palm = dist(lm, 0, 9)

        # Finger status (tips lebih tinggi dari pip = terbuka)
        t  = dist(lm, 4, 17) > palm * 1.05     # Jempol
        i  = lm[8].y < lm[6].y                  # Telunjuk
        m  = lm[12].y < lm[10].y                # Tengah
        r  = lm[16].y < lm[14].y                # Manis
        p  = lm[20].y < lm[18].y                # Kelingking

        # ── SUKSES: Hanya jempol ke atas ─────────────────────────────────────
        if t and not i and not m and not r and not p:
            detected = "Sukses"

        # ── BERJUANG: Semua jari mengepal (tinju) ────────────────────────────
        elif not t and not i and not m and not r and not p:
            detected = "Berjuang"

        # ── SELAMAT: Jempol + Telunjuk + Kelingking terbuka (like ILY / Metal)
        elif t and i and p and not m and not r:
            detected = "Selamat"

    # ── Stabilizer ───────────────────────────────────────────────────────────
    if detected:
        gesture_counter[detected] = gesture_counter.get(detected, 0) + 1
        if gesture_counter[detected] >= STABLE_FRAMES:
            stable_gesture = detected
    else:
        gesture_counter.clear()
        stable_gesture = ""

    # ── Speak ─────────────────────────────────────────────────────────────────
    now = time.time()
    if (stable_gesture
            and stable_gesture != last_gesture
            and now - last_speak_time > SPEAK_COOLDOWN):
        speak(stable_gesture)
        last_gesture    = stable_gesture
        last_speak_time = now

    # ── UI ────────────────────────────────────────────────────────────────────
    style  = GESTURE_STYLE.get(stable_gesture, {"color": (200, 200, 200)})
    color  = style["color"]

    # Header bar
    cv2.rectangle(frame, (0, 0), (w, 65), UI_BG, -1)
    cv2.putText(frame, "Mode Jokowi",
                (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, UI_DIM, 1)

    # Gestur label besar
    label = stable_gesture if stable_gesture else "—"
    cv2.putText(frame, label,
                (12, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

    # Confidence bar
    conf  = min(gesture_counter.get(stable_gesture, 0), STABLE_FRAMES)
    bar_w = int((conf / STABLE_FRAMES) * 200)
    cv2.rectangle(frame, (w - 220, 20), (w - 20, 40), (40, 40, 40), -1)
    cv2.rectangle(frame, (w - 220, 20), (w - 220 + bar_w, 40), color, -1)
    cv2.putText(frame, "Confidence",
                (w - 220, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, UI_DIM, 1)

    # Legend
    legend_items = [("👍 Sukses", "Jempol ke atas"),
                    ("✊ Berjuang", "Tinju rapat"),
                    ("🤟 Selamat", "Jempol+Telunjuk+Kelingking")]
    for li, (lg_label, lg_desc) in enumerate(legend_items):
        ly = h - 28 - li * 22
        cv2.putText(frame, f"{lg_label}: {lg_desc}",
                    (10, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.42, UI_DIM, 1)

    # Footer
    cv2.rectangle(frame, (0, h - 30), (w, h), UI_BG, -1)
    cv2.putText(frame, "Q = Keluar",
                (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, UI_DIM, 1)

    cv2.imshow("Mode Jokowi — SensorKamera", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
cleanup_mp3()
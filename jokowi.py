import os
import cv2
import time
import math
import threading
import mediapipe as mp
from gtts import gTTS
from pygame import mixer

# ----------------- SETUP -----------------
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=1, # Fokus 1 tangan saja sesuai permintaan
    min_detection_confidence=0.8, 
    min_tracking_confidence=0.8
)
mixer.init()

def speak(text):
    def run():
        fname = f"suara_{int(time.time()*1000)}.mp3"
        try:
            tts = gTTS(text=text, lang="id")
            tts.save(fname)
            mixer.music.load(fname)
            mixer.music.play()
            while mixer.music.get_busy(): time.sleep(0.1)
            mixer.music.unload() 
            if os.path.exists(fname): os.remove(fname)
        except: pass
    threading.Thread(target=run, daemon=True).start()

def cleanup():
    for f in os.listdir("."):
        if f.startswith("suara_") and f.endswith(".mp3"):
            try: os.remove(f)
            except: pass

def get_dist(lm, idx1, idx2):
    return math.hypot(lm[idx1].x - lm[idx2].x, lm[idx1].y - lm[idx2].y)

# ----------------- INIT -----------------
cleanup()
cap = cv2.VideoCapture(0)
last_gesture, last_speak_time = "", 0
gesture_counter, stable_gesture = {}, ""

print("[SISTEM] Mode Khusus: Selamat, Berjuang, Sukses Aktif!")

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    detected = ""

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        lm = hand.landmark
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        
        palm = get_dist(lm, 0, 9)

        # Status Jari
        up4 = get_dist(lm, 4, 17) > palm * 1.1 # Jempol terbuka
        up8 = get_dist(lm, 8, 0) > palm * 1.3  # Telunjuk
        up12 = get_dist(lm, 12, 0) > palm * 1.3 # Tengah
        up16 = get_dist(lm, 16, 0) > palm * 1.3 # Manis
        up20 = get_dist(lm, 20, 0) > palm * 1.3 # Kelingking

        # ---------- LOGIKA KHUSUS JOKOWI ----------

        # 1. SUKSES (Hanya Jempol ke atas, jari lain mengepal)
        if up4 and not up8 and not up12 and not up16 and not up20:
            detected = "Sukses"

        # 2. BERJUANG (Semua jari mengepal rapat / Tinju)
        elif not up4 and not up8 and not up12 and not up16 and not up20:
            detected = "Berjuang"

        # 3. SELAMAT (Gestur Metal: Jempol, Telunjuk, Kelingking lurus)
        elif up4 and up8 and up20 and not up12 and not up16:
            detected = "Selamat"

    # ---------- STABILIZER ----------
    if detected:
        gesture_counter[detected] = gesture_counter.get(detected, 0) + 1
        if gesture_counter[detected] >= 5: stable_gesture = detected
    else:
        gesture_counter.clear()
        stable_gesture = ""

    # ---------- AUDIO ----------
    now = time.time()
    if stable_gesture and stable_gesture != last_gesture and now - last_speak_time > 2:
        speak(stable_gesture)
        last_gesture, last_speak_time = stable_gesture, now

    # ---------- UI ----------
    cv2.rectangle(frame, (0, 0), (400, 60), (0, 0, 0), -1)
    cv2.putText(frame, f"STATUS: {stable_gesture}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Mode Khusus Jokowi", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break

cap.release()
cv2.destroyAllWindows()
cleanup()
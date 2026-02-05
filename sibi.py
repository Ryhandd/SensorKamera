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
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mixer.init()

# ----------------- AUDIO -----------------
def speak(text):
    def run():
        fname = f"sibi_{int(time.time()*1000)}.mp3"
        try:
            gTTS(text=text, lang="id").save(fname)
            mixer.music.load(fname)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.1)
            mixer.music.unload()
            if os.path.exists(fname): os.remove(fname)
        except:
            pass
    threading.Thread(target=run, daemon=True).start()

# ----------------- UTIL -----------------
def cleanup():
    for f in os.listdir("."):
        if f.startswith("sibi_") and f.endswith(".mp3"):
            try: os.remove(f)
            except: pass

# --- FUNGSI PENTING: MENGHITUNG JARAK ANTAR TITIK JARI ---
def get_dist(lm, idx1, idx2):
    return math.hypot(lm[idx1].x - lm[idx2].x, lm[idx1].y - lm[idx2].y)

def is_index_pointing(lm):
    return lm[8].y < lm[6].y

# ----------------- INIT -----------------
cleanup()
cap = cv2.VideoCapture(0)

last_gesture = ""
last_speak_time = 0

GESTURE_STABLE_FRAMES = 5
gesture_counter = {}
stable_gesture = ""

TWO_HAND_HOLD_FRAMES = 6
two_hand_counter = 0

prev_wrist = None

print("[INFO] SIBI Reader Aktif")

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    detected = ""

    if result.multi_hand_landmarks:
        hands_count = len(result.multi_hand_landmarks)

        # ========== GESTUR 2 TANGAN (NAMA) ==========
        if hands_count >= 2:
            lm1 = result.multi_hand_landmarks[0].landmark
            lm2 = result.multi_hand_landmarks[1].landmark

            pointer, base = None, None
            if is_index_pointing(lm1):
                pointer, base = lm1, lm2
            elif is_index_pointing(lm2):
                pointer, base = lm2, lm1

            if pointer:
                dist = abs(pointer[8].x - base[5].x) + abs(pointer[8].y - base[8].y)
                if dist < 0.45:
                    two_hand_counter += 1
                    if two_hand_counter >= TWO_HAND_HOLD_FRAMES:
                        detected = "Nama"
                else:
                    two_hand_counter = 0
        else:
            two_hand_counter = 0

        # ========== 1 HAND (FINAL STABLE LOGIC) ==========
        if hands_count == 1 and detected == "":
            hand = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            lm = hand.landmark
            palm = get_dist(lm, 0, 9)

            # --- 1. LOGIKA "H" (PRIORITAS HORIZONTAL) ---
            # Menggunakan selisih koordinat X dan Y ujung telunjuk(8) & tengah(12)
            #
            x_dist_8 = abs(lm[8].x - lm[5].x)
            y_dist_8 = abs(lm[8].y - lm[5].y)
            x_dist_12 = abs(lm[12].x - lm[9].x)
            y_dist_12 = abs(lm[12].y - lm[9].y)

            # Syarat H: Jari memanjang ke samping (X > Y) dan cukup lurus
            if x_dist_8 > y_dist_8 and x_dist_12 > y_dist_12 and x_dist_8 > palm * 0.7:
                detected = "H"

            # --- 2. JIKA BUKAN H, LANJUT KE GESTUR LAIN ---
            if detected == "":
                # Status Jari
                up4  = get_dist(lm, 4, 17) > palm * 1.1 # Jempol terbuka
                up8  = lm[8].y < lm[6].y  # Telunjuk tegak
                up12 = lm[12].y < lm[10].y # Tengah tegak
                up16 = lm[16].y < lm[14].y # Manis tegak
                up20 = lm[20].y < lm[18].y # Kelingking tegak

                # --- SAYA vs Y (Berdasarkan Sisi Tangan) ---
                if up4 and up20 and not up8 and not up12 and not up16:
                    if lm[4].x < lm[20].x: 
                        detected = "Saya" # Punggung tangan menghadap kamera
                    else:
                        detected = "Y"    # Telapak depan menghadap kamera

                # --- D (TELUNJUK TEGAK) ---
                # Syarat: Hanya telunjuk lurus, jari lain tekuk melingkar
                elif up8 and not up12 and not up16 and not up20:
                    detected = "D"

                # --- A, E, vs N (KEPALAN TANGAN) ---
                elif not up8 and not up12 and not up16 and not up20:
                    # N: Jempol di sela Telunjuk dan Tengah
                    if lm[5].x < lm[4].x < lm[9].x:
                        detected = "N"
                    # A: Jempol di samping luar pangkal telunjuk
                    elif lm[4].x > lm[5].x or lm[4].y < lm[5].y:
                        detected = "A"
                    else:
                        detected = "E"

                # --- ALFABET LAINNYA ---
                elif up8 and up12 and not up16 and not up20:
                    if abs(lm[8].x - lm[12].x) > 0.05: detected = "V"
                    else: detected = "R"
                elif up8 and up12 and up16 and not up20: detected = "W"
                elif up8 and up4 and not up12: detected = "L"
                elif up20 and not up8 and not up12 and not up16: detected = "I"
                elif get_dist(lm, 4, 8) < palm * 0.4 and not up12: detected = "O"
                elif palm * 0.4 < get_dist(lm, 4, 8) < palm * 0.9 and not up12:
                    # Pastikan telapak tangan tegak untuk C
                    if abs(lm[5].y - lm[0].y) > abs(lm[5].x - lm[0].x):
                        detected = "C"

    # ---------- STABILIZER ----------
    if detected:
        gesture_counter[detected] = gesture_counter.get(detected, 0) + 1
        if gesture_counter[detected] >= GESTURE_STABLE_FRAMES:
            stable_gesture = detected
    else:
        gesture_counter.clear()
        stable_gesture = ""

    # ---------- SPEAK ----------
    now = time.time()
    if stable_gesture and stable_gesture != last_gesture and now - last_speak_time > 2:
        speak(stable_gesture)
        last_gesture = stable_gesture
        last_speak_time = now

    # ---------- UI ----------
    cv2.rectangle(frame, (0, 0), (320, 50), (0, 0, 0), -1)
    cv2.putText(frame, f"SIBI: {stable_gesture}", (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("SIBI Reader - Indonesia", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
cleanup()
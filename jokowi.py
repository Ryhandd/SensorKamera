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

# ----------------- CLEANUP -----------------
def cleanup():
    for f in os.listdir("."):
        if f.startswith("sibi_") and f.endswith(".mp3"):
            try: os.remove(f)
            except: pass

# ----------------- HELPER FUNCTIONS -----------------
def get_dist(lm, idx1, idx2):
    return math.hypot(lm[idx1].x - lm[idx2].x, lm[idx1].y - lm[idx2].y)

# ----------------- INIT -----------------
cleanup()
cap = cv2.VideoCapture(0)

last_gesture = ""
last_speak_time = 0
gesture_counter = {}
stable_gesture = ""
GESTURE_STABLE_FRAMES = 5
TWO_HAND_HOLD_FRAMES = 6
two_hand_counter = 0

print("[INFO] SIBI Reader Aktif - V4.0 Horizontal Fix")

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    detected = ""

    if result.multi_hand_landmarks:
        # ========== GESTUR 2 TANGAN (NAMA) ==========
        if len(result.multi_hand_landmarks) >= 2:
            h1 = result.multi_hand_landmarks[0].landmark
            h2 = result.multi_hand_landmarks[1].landmark
            
            # Cek tumpukan telunjuk (kanan di atas kiri)
            dist_cross = math.hypot(h1[8].x - h2[5].x, h1[8].y - h2[5].y)
            dist_touch = math.hypot(h1[8].x - h2[8].x, h1[8].y - h2[8].y)
            
            if dist_cross < 0.15 or dist_touch < 0.1:
                two_hand_counter += 1
                if two_hand_counter >= TWO_HAND_HOLD_FRAMES:
                    detected = "Nama"
            else:
                two_hand_counter = 0
        else:
            two_hand_counter = 0

        # ========== GESTUR 1 TANGAN (ALFABET) ==========
        if detected == "":
            hand = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            lm = hand.landmark
            
            # --- UKURAN TANGAN (Reference) ---
            # Jarak Pergelangan(0) ke Pangkal Jari Tengah(9)
            palm_size = get_dist(lm, 0, 9) 

            # --- ANALISIS JARI (LURUS/TEKUK) ---
            # Jari dianggap LURUS jika jarak Ujung ke Pergelangan > 1.3x ukuran telapak
            fingers = []
            for tip_id in [8, 12, 16, 20]: # Telunjuk s/d Kelingking
                if get_dist(lm, tip_id, 0) > palm_size * 1.3:
                    fingers.append(True)  # Lurus
                else:
                    fingers.append(False) # Tekuk
            
            # Jempol: Cek jarak ke Kelingking (biar tau dia kebuka atau nempel)
            thumb_open = get_dist(lm, 4, 17) > palm_size * 1.0

            # Mapping jari: [Telunjuk, Tengah, Manis, Kelingking]
            idx, mid, rng, pnk = fingers

            # --- LOGIKA PRIORITAS TINGGI (KHUSUS H) ---
            
            # GESTUR 'H' (Dua Jari Menyamping)
            # Syarat 1: Telunjuk & Tengah LURUS, Manis & Kelingking TEKUK
            if idx and mid and not rng and not pnk:
                # Syarat 2: WAJIB HORIZONTAL
                # Cek jarak horizontal (X) ujung telunjuk ke pangkalnya
                x_len = abs(lm[8].x - lm[5].x)
                y_len = abs(lm[8].y - lm[5].y)
                
                # Jika X jauh lebih panjang dari Y, berarti menyamping
                if x_len > y_len * 1.5: 
                    detected = "H"
                # Jika tegak lurus (Y lebih panjang), berarti U/V
                elif y_len > x_len:
                    # Bedakan U (Rapat) dan V (Pisah)
                    if get_dist(lm, 8, 12) > palm_size * 0.4:
                        detected = "V"
                    else:
                        detected = "U" 

            # GESTUR 'G' (Satu Jari Menyamping)
            # Syarat: Telunjuk LURUS, sisanya TEKUK
            elif idx and not mid and not rng and not pnk:
                x_len = abs(lm[8].x - lm[5].x)
                y_len = abs(lm[8].y - lm[5].y)
                
                # Cek Horizontal untuk G
                if x_len > y_len * 1.5:
                    detected = "G"
                elif y_len > x_len: # Tegak lurus
                    detected = "D"

            # --- LOGIKA UMUM ---

            # GESTUR 'A' (Kepal)
            # Syarat: SEMUA jari (Telunjuk-Kelingking) TEKUK
            elif not idx and not mid and not rng and not pnk:
                # Cek Jempol: Harus nempel di samping (Y ujung < Y pangkal dikit atau sejajar)
                # Pastikan jempol tidak masuk ke dalam (seperti E/S)
                if lm[4].y < lm[6].y: 
                    detected = "A"
                else:
                    detected = "E" # Bisa juga S/M/N tergantung detail jempol

            # GESTUR 'O'
            # Ujung Jempol ketemu Ujung Telunjuk
            elif get_dist(lm, 4, 8) < palm_size * 0.3 and not mid:
                 detected = "O"

            # GESTUR 'C'
            # Mulut C terbuka lebar
            elif get_dist(lm, 4, 8) > palm_size * 0.4 and not mid and not rng:
                detected = "C"

            # GESTUR 'B' (4 Jari Tegak)
            elif idx and mid and rng and pnk:
                detected = "B"

            # GESTUR 'L' (Jempol & Telunjuk Tegak)
            elif idx and thumb_open and not mid:
                detected = "L"

            # GESTUR 'I' (Kelingking Tegak)
            elif pnk and not idx and not mid and not rng:
                detected = "I"
                
            # GESTUR 'Y' / 'Saya'
            elif pnk and thumb_open and not idx and not mid:
                detected = "Saya"
            
            # GESTUR 'F' (OK Sign)
            elif not idx and mid and rng and pnk: # Telunjuk ditekuk (ketemu jempol), sisa lurus
                detected = "F"

    # ---------- STABILIZER ----------
    if detected:
        gesture_counter[detected] = gesture_counter.get(detected, 0) + 1
        if gesture_counter[detected] >= GESTURE_STABLE_FRAMES:
            stable_gesture = detected
    else:
        gesture_counter.clear()

    # ---------- SPEAK ----------
    now = time.time()
    if stable_gesture and stable_gesture != last_gesture:
        if now - last_speak_time > 2.0: 
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
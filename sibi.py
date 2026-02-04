import os
import cv2
import time
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
            os.remove(fname)
        except:
            pass
    threading.Thread(target=run, daemon=True).start()

# ----------------- UTIL -----------------
def cleanup():
    for f in os.listdir("."):
        if f.startswith("sibi_") and f.endswith(".mp3"):
            try: os.remove(f)
            except: pass

def is_index_pointing(lm):
    return lm[8].y < lm[6].y

def is_palm_open(lm):
    return (
        lm[8].y < lm[6].y and
        lm[12].y < lm[10].y
    )

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
        else:
            two_hand_counter = 0

        # ========== 1 HAND ==========
        if hands_count == 1 and detected == "":
            hand = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            lm = hand.landmark

            wrist = lm[0]
            movement = 0
            if prev_wrist:
                movement = abs(wrist.x - prev_wrist.x) + abs(wrist.y - prev_wrist.y)
            prev_wrist = wrist

            up4  = lm[4].y  < lm[3].y
            up8  = lm[8].y  < lm[6].y
            up12 = lm[12].y < lm[10].y
            up16 = lm[16].y < lm[14].y
            up20 = lm[20].y < lm[18].y

            # Saya / Y
            if up4 and up20 and not up8 and not up12 and not up16:
                detected = "Saya" if movement > 0.02 else "Y"

            # V
            elif up8 and up12 and not up16 and not up20 and abs(lm[8].x - lm[12].x) > 0.06:
                detected = "V"

            # W
            elif up8 and up12 and up16 and not up20:
                detected = "W"

            # R
            elif up8 and up12 and abs(lm[8].x - lm[12].x) < 0.03:
                detected = "R"

            # L
            elif up8 and up4 and not up12 and not up16 and not up20:
                detected = "L"

            # K
            elif up8 and up12 and lm[4].y < lm[10].y:
                detected = "K"

            # D
            elif up8 and not up12 and not up16 and not up20:
                detected = "D"

            # B
            elif up8 and up12 and up16 and up20 and lm[4].x > lm[6].x:
                detected = "B"

            # A
            elif (
                lm[8].y > lm[6].y and
                lm[12].y > lm[10].y and
                lm[16].y > lm[14].y and
                lm[20].y > lm[18].y and
                (lm[8].z > lm[5].z - 0.01) and
                lm[4].x > lm[3].x
            ):
                detected = "A"
                
            # H
            elif (
                lm[8].y > lm[6].y and
                lm[12].y > lm[10].y and
                lm[16].y > lm[14].y and
                (lm[8].z < lm[5].z - 0.03) and
                (lm[12].z < lm[9].z - 0.03)
            ):
                detected = "H"

            # F
            elif (
                abs(lm[4].x - lm[8].x) < 0.04 and
                up12 and up16 and up20
            ):
                detected = "F"

            # I
            elif up20 and not up8 and not up12 and not up16:
                detected = "I"

            # O
            elif abs(lm[4].x - lm[8].x) < 0.05 and not up12:
                detected = "O"

            # E
            elif (lm[8].y > lm[6].y and
                  lm[12].y > lm[10].y and
                  lm[16].y > lm[14].y and
                  lm[20].y > lm[18].y and
                  lm[4].x < lm[3].x):
                detected = "E"

            # C (PALING BAWAH)
            elif abs(lm[4].x - lm[8].x) > 0.12 and up8:
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

# ----------------- CLEAN -----------------
cap.release()
cv2.destroyAllWindows()
cleanup()

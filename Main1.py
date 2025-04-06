import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import subprocess
import time
import pyttsx3

# Initialize TTS
engine = pyttsx3.init()

# Webcam
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Detectors
face_detector = FaceMeshDetector(maxFaces=1)
hand_detector = HandDetector(detectionCon=0.8, maxHands=1)

# Screen size
screen_w, screen_h = pyautogui.size()

# Gesture state tracking
last_action_time = time.time()
action_cooldown = 1.0  # seconds

def can_perform_action():
    return time.time() - last_action_time > action_cooldown

while True:
    try:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        frame, faces = face_detector.findFaceMesh(frame, draw=True)
        hands, frame = hand_detector.findHands(frame, draw=True)

        # ===== FACE MOUSE CONTROL =====
        if faces:
            face = faces[0]
            x = (face[33][0] + face[263][0]) // 2
            y = (face[33][1] + face[263][1]) // 2
            pyautogui.moveTo(1.5 * screen_w * x / frame.shape[1], 1.5 * screen_h * y / frame.shape[0])

            left_eye = abs(face[145][1] - face[159][1])
            right_eye = abs(face[374][1] - face[386][1])

            # Left Click
            if left_eye < 4 and right_eye > 6 and can_perform_action():
                engine.say("Left Click")
                engine.runAndWait()
                pyautogui.click()
                last_action_time = time.time()

            # Right Click
            elif right_eye < 4 and left_eye > 6 and can_perform_action():
                engine.say("Right Click")
                engine.runAndWait()
                pyautogui.rightClick()
                last_action_time = time.time()

        # ===== HAND GESTURE CONTROL =====
        if hands:
            hand = hands[0]
            lmList = hand["lmList"]
            fingers = hand_detector.fingersUp(hand)

            # Screenshot: index and middle fingers only
            if fingers == [0, 1, 1, 0, 0] and can_perform_action():
                engine.say("Taking Screenshot")
                engine.runAndWait()
                pyautogui.screenshot('screenshot_hand.png')
                last_action_time = time.time()

            # Scroll Up: index only up and moving up
            elif fingers == [0, 1, 0, 0, 0] and (lmList[8][1] < lmList[6][1] - 20) and can_perform_action():
                engine.say("Scroll Up")
                engine.runAndWait()
                pyautogui.scroll(20)
                last_action_time = time.time()

            # Scroll Down: index only up and moving down
            elif fingers == [0, 1, 0, 0, 0] and (lmList[8][1] > lmList[6][1] + 20) and can_perform_action():
                engine.say("Scroll Down")
                engine.runAndWait()
                pyautogui.scroll(-20)
                last_action_time = time.time()

            # Open Chrome: All 5 fingers up
            elif fingers == [1, 1, 1, 1, 1] and can_perform_action():
                engine.say("Opening Chrome")
                engine.runAndWait()
                subprocess.Popen("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
                last_action_time = time.time()

            # Exit: Only thumb up
            elif fingers == [1, 0, 0, 0, 0] and can_perform_action():
                engine.say("Exiting")
                engine.runAndWait()
                break

        cv2.imshow("Eye & Hand Controlled Mouse", frame)
        time.sleep(0.05)

    except Exception as e:
        print(f"Error: {e}")

    if cv2.waitKey(1) & 0xFF == ord('c'):
        break

cap.release()
cv2.destroyAllWindows()

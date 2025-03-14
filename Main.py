import cv2
import mediapipe as mp
import pyautogui
import subprocess
import time 
import pyttsx3

engine = pyttsx3.init()
vid = cv2.VideoCapture(1,cv2.CAP_DSHOW)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()
blink_start_time = None
blink_duration_threshold = 0.3 
while True:
    try:
        ret,frame = vid.read()
        if not ret:
            print("Failed to capture frame")
            continue
        frame = cv2.flip(frame, 1)
        frame_h, frame_w, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks

        if(landmark_points):
            landmarks = landmark_points[0].landmark
            for right_eye in range(474,478):
                x = int((landmarks[right_eye].x) * frame_w)
                y = int((landmarks[right_eye].y) * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                if(right_eye == 476):
                    pos_x = screen_w * landmarks[right_eye].x
                    pos_y = screen_h * landmarks[right_eye].y
                    pyautogui.moveTo(pos_x,pos_y) # Move the cursor

            left_eye = [landmarks[145], landmarks[159]]
            for i in left_eye: 
                x = int((i.x) * frame_w)
                y = int((i.y) * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 254, 0))

            if ((left_eye[0].y - left_eye[1].y) < 0.004 and (landmarks[374].y - landmarks[386].y) > 0.009):
                engine.say("Left Click")
                engine.runAndWait()
                pyautogui.click()
                pyautogui.sleep(1)

            elif ((landmarks[374].y - landmarks[386].y) < 0.004) and ((left_eye[0].y - left_eye[1].y) > 0.009):
                engine.say("right Click")
                engine.runAndWait()
                pyautogui.rightClick()
                pyautogui.sleep(1)
            
            elif landmarks[1].y < 0.3: # Nose Tip
                engine.say("Scroll up")
                engine.runAndWait()
                pyautogui.scroll(10) 
            elif landmarks[1].y > 0.69:
                engine.say("Scroll down")
                engine.runAndWait()  
                pyautogui.scroll(-10)
            
            elif (landmarks[14].y - landmarks[13].y) > 0.05:
                engine.say("Taking Screenshot")
                engine.runAndWait()
                pyautogui.screenshot('screenshot.png')
                time.sleep(1)
            
            left_mouth = landmarks[61]  # Left corner of mouth
            right_mouth = landmarks[291]  # Right corner of mouth
            top_lip = landmarks[13]  # Top lip
            bottom_lip = landmarks[14]  # Bottom lip

            mouth_width = abs(left_mouth.x - right_mouth.x)
            if mouth_width > 0.095:
                subprocess.Popen("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
                engine.say("Smiling")
                engine.runAndWait()
            
            left_eye_blink = (left_eye[0].y - left_eye[1].y) < 0.004
            right_eye_blink = (landmarks[374].y - landmarks[386].y) < 0.004
            if left_eye_blink and right_eye_blink:
                if not blink_start_time:
                    blink_start_time = time.time()
                elif time.time() - blink_start_time > blink_duration_threshold:
                    engine.say("Exiting")
                    engine.runAndWait()
                    exit(0) # close both of your eyes for some time to exit
            else:
                blink_start_time = None

        cv2.imshow("Eye Controlled Mouse",frame)
        time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")
    if(cv2.waitKey(1) & 0xff==ord('c')):
        break
vid.release()
cv2.destroyAllWindows()


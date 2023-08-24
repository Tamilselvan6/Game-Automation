import cv2
import mediapipe as mp
import time
from directkeys import right_pressed, left_pressed
from directkeys import PressKey, ReleaseKey

# Define the key names for better readability
break_key_pressed = left_pressed
accelerator_key_pressed = right_pressed

# Sleep for 2 seconds to give time for the user to position their hand
time.sleep(2.0)

current_key_pressed = set()

mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

tipIds = [4, 8, 12, 16, 20]

video = cv2.VideoCapture(0)

with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        keyPressed = False
        break_pressed = False
        accelerator_pressed = False
        key_count = 0
        key_pressed = 0
        ret, image = video.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        lmList = []
        if results.multi_hand_landmarks:
            for hand_landmark in results.multi_hand_landmarks:
                myHands = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHands.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)
        fingers = []
        if len(lmList) != 0:
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            total = fingers.count(1)
            if total == 0:
                # Draw Brake overlay
                cv2.putText(image, "BRAKE", (50, 380), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2, lineType=cv2.LINE_AA)
                PressKey(break_key_pressed)
                break_pressed = True
                current_key_pressed.add(break_key_pressed)
                key_pressed = break_key_pressed
                keyPressed = True
                key_count = key_count + 1
            elif total == 5:
                # Draw Accelerator overlay)
                cv2.putText(image, "GAS", (50, 380), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2, lineType=cv2.LINE_AA)
                PressKey(accelerator_key_pressed)
                key_pressed = accelerator_key_pressed
                accelerator_pressed = True
                keyPressed = True
                current_key_pressed.add(accelerator_key_pressed)
                key_count = key_count + 1
        if not keyPressed and len(current_key_pressed) != 0:
            for key in current_key_pressed:
                ReleaseKey(key)
            current_key_pressed = set()
        elif key_count == 1 and len(current_key_pressed) == 2:
            for key in current_key_pressed:
                if key_pressed != key:
                    ReleaseKey(key)
            current_key_pressed = set()

        # Add additional text information to guide the user
        cv2.putText(image, "Raise all 5 fingers to accelerate", (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2, lineType=cv2.LINE_AA)
        cv2.putText(image, "Close all fingers to brake", (20, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2, lineType=cv2.LINE_AA)
        cv2.putText(image, "Press 'q' to exit", (20, 90), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2, lineType=cv2.LINE_AA)

        cv2.imshow("Hand Gesture Controller", image)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
video.release()
cv2.destroyAllWindows()

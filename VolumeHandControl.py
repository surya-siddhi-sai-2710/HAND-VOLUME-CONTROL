import math
import cv2
import mediapipe as mp
import time
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

########################
#size of the camera window
wCam, hCam = 640, 480
########################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
vol = 0
VolBar = 400
VolPer = 0

detector = htm.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]



while True:
    success, img = cap.read()
    detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])


        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2 , (y1 + y2) // 2


        cv2.circle(img,(x1,y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1,y1),(x2,y2),(255,0,255),3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1,y2 - y1)
        #print(length)

        # Hand Range 50 - 300
        # Volume Range -65 - 0

        Vol = np.interp(length, [50, 300], [minVol, maxVol])
        VolBar = np.interp(length, [50, 300], [400, 150])
        VolPer = np.interp(length, [50, 300], [0, 100])
        print(int(length), Vol)
        volume.SetMasterVolumeLevel(Vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)


    # creating rectangle bar to show the volume level
    cv2.rectangle(img, (50,150), (85,400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(VolBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(VolPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)



    cTime = time.time()
    fps = 1/ (cTime-pTime)
    pTime = cTime

    cv2.putText(img,f'FPS: {int(fps)}', (40,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)


    cv2.imshow("image", img)
    cv2.waitKey(1)
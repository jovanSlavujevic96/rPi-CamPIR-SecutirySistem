import numpy as np
import cv2

cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
#fourcc = cv2.cv.CV_FOURCC(*'DIVX')
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
# out = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))

from threading import Thread
import threading
import time

bRecordVideo = True
bDetected = True

from datetime import datetime

def VideoWriting():
    global frame
    global bWriteVideo
    bFirstTime = True
    bWriteVideo = False
    out = cv2.VideoWriter()
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G') #cv2.VideoWriter_fourcc(*'XVID')

    while bRecordVideo:
        if(True == bFirstTime and True == bDetected and True == bWriteVideo):
            fileName = datetime.now().strftime("%Y_%m_%d-%H_%M_%S") + '.avi'
            out = cv2.VideoWriter(fileName, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4)))) 
            #cv2.VideoWriter('output.avi',fourcc, 20.0, (frame.shape[0],frame.shape[1]) )
            print(out.getBackendName())
            bFirstTime = False
        if(True == bWriteVideo):
            out.write(frame)
            bWriteVideo = False
        if(False == bDetected):
            bFirstTime = True
            out.release()
    
    if(out.isOpened() ):
        out.release()

recordingVideoThread = Thread(target=VideoWriting)

recordingVideoThread.daemon = True
recordingVideoThread.start()

ret = False
while(cap.isOpened()):
    try:
        ret, frame = cap.read()
    except KeyboardInterrupt:
        break

    if ret==True:
        bWriteVideo = True
        cv2.imshow('frame',frame)
        key = cv2.waitKey(1) 
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('s'):
            bDetected = not bDetected
    else:
        break

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()

bRecordVideo = False

recordingVideoThread.join()

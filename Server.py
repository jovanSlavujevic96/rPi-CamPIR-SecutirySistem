#face detection dependencies
import cv2
import numpy as np

#TCP/IP socket communication dependencies
import socket
from threading import Thread
import threading
import time

#sys lib for checking a platform (OS)
from sys import platform

import struct
import pickle

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

#face detection classifier
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#WebCam handler
if platform == "linux" or platform == "linux2":
    cap = cv2.VideoCapture(0)
elif platform == "win32":
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 320)
cap.set(4, 240)

#socket server's IP address & port 
port = 21000
host = socket.gethostname() # Get local machine name

#socket initialisation
clients = set()
clients_lock = threading.Lock()

serversock = socket.socket()
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind((host,port))
serversock.listen(3)
th = []

ClientConnection = True

def listener(client, address):
    global data
    global sndMsg
    print ("\nAccepted connection from: ", address,'\n')
    with clients_lock:
        clients.add(client)

    while ClientConnection:
        if sndMsg == True:
            try:
                client.sendall(struct.pack(">L", len(data) ) + data)
                sndMsg = False
            except BrokenPipeError:
                break
    
    print("\nBroken connection from: ", address, "\n")
    clients.remove(client)

def clientReceivement():
    global sndMsg
    sndMsg = False

    print ("\nWaiting for new clients...\n")
    while True:
        try:
           (client, address) = serversock.accept()
        except OSError:
            break

        th.append(Thread(target=listener, args = (client,address)) )
        th[-1].start()
    

th.append(Thread(target=clientReceivement) )
th[-1].start()


incr = 0
limit = 40000

while True:
    try:        
        incr = incr + 1

        if(incr < limit):
            continue
        elif(incr == limit):
            incr = 0

        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for(x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 255), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

        # cv2.imshow('img', frame)
        # k = cv2.waitKey(30) & 0xff
        # if k == 27:
        #     break

        # if(len(faces) == 0):
        #     continue

        sndMsg = True
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(frame, 0)

    except KeyboardInterrupt:
        break

cap.release()
cv2.destroyAllWindows()

for client in clients:
    client.shutdown(socket.SHUT_RDWR)
    client.close()

ClientConnection = False

try:
    serversock.shutdown(socket.SHUT_RDWR)
    serversock.close()
except OSError:
    serversock.close()


if(clients_lock.locked() == True):
    clients_lock.release()

for thd in th:
    thd.join()

print("\nSuccessfully closed server application\n")
exit() 
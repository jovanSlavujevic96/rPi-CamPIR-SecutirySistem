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

#face detection classifier
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#WebCam handler
if platform == "linux" or platform == "linux2":
    cap = cv2.VideoCapture(0)
elif platform == "win32":
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#socket server's IP address & port 
port = 21000
host = socket.gethostname() # Get local machine name

#socket initialisation
clients = set()
clients_lock = threading.Lock()

global serversock
serversock = socket.socket()
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind((host,port))
serversock.listen(3)
th = []

def listener(client, address):
    global img
    print ("\nAccepted connection from: ", address,'\n')
    with clients_lock:
        clients.add(client)
    try:    
        while True:
            data = client.recv(1024)
            if int(data) == 0:
                msg = "HI :)"
                print('\nSENDING: ', str(msg),'\n')
                #char = str(int(catch))
                client.send(bytes(msg,encoding='utf8'))
    except ValueError:
        print("\nClient Disconnected\n")

def clientReceivement():

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
while True:
    global img
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for(x, y, w, h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0, 0, 255), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

    cv2.imshow('img', img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()

try:
    serversock.shutdown(socket.SHUT_RDWR)
    serversock.close()
except OSError:
    serversock.close()

for thd in th:
    thd.join()

print("\nSuccessfully closed server application\n")
exit() 
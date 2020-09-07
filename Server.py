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

#support libraries for image packing
import struct
import pickle

#RPi lib for distance measurement usecase
import RPi.GPIO as GPIO
import time

def HCSR04_init():
    #GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)
    
    #set GPIO Pins
    GPIO_TRIGGER = 18
    GPIO_ECHO = 24

    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def HCSR04_loop():
    global detected
    detected = False
    itterations = 0 #til itterationLimit
    itterationLimit = 100
    distanceLimit = 80.0
    while True:
        dist = distance()
        print ("Measured Distance = %.1f cm" % dist)
        if(dist < distanceLimit):
            detected = True
        if(True == detected):
            itterations += 1
        if(itterations == itterationLimit):
            itterations = 0
            detected = False
        time.sleep(1)

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

#arguments parser for IP address enter
import argparse

parser = argparse.ArgumentParser(description='set the IP address.')
parser.add_argument('--IP', type=str, help='set the IP address of the rPi (server device)')
args = parser.parse_args()

#socket server's IP address & port 
port = 21000
host = str(args.IP) #'192.168.0.109' #socket.gethostname() # Get local machine name

#socket initialisation
clients = set()
clients_lock = threading.Lock()

serversock = socket.socket()
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind((host,port))
serversock.listen(3)

print("IP: ")
print(serversock.getsockname() )

th = []

ClientConnection = True

def listener(client, address):
    global data
    global detected
    sndMsg = False
    print ("\nAccepted connection from: ", address,'\n')
    with clients_lock:
        clients.add(client)

    while ClientConnection:
        if sndMsg == True and detected == True:
            try:
                client.sendall(struct.pack(">L", len(data) ) + data)
                sndMsg = False
            except BrokenPipeError:
                break
            except ConnectionResetError:
                break
            except ConnectionAbortedError:
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
    

HCSR04_init()
th.append(Thread(target=HCSR04_loop))

th.append(Thread(target=clientReceivement) )
th[-1].start()

incr = 0
limit = 40000

global detected
while True:
    try:        
        incr = incr + 1

        if(incr < limit):
            continue
        elif(incr == limit):
            incr = 0

        ret, frame = cap.read()

        if detected == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for(x, y, w, h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 255), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
            
            sndMsg = True
            result, frame = cv2.imencode('.jpg', frame, encode_param)
            data = pickle.dumps(frame, 0)


        # #display image and handle break with escape button
        # cv2.imshow('img', frame)
        # k = cv2.waitKey(30) & 0xff
        # if k == 27:
        #     break

        # #enable only sending frames with frame detection
        # if(len(faces) == 0):
        #     continue

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
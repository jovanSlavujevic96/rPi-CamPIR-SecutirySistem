import cv2
# import io
import socket
import struct
import time
import pickle
import zlib

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

import argparse

parser = argparse.ArgumentParser(description='set the IP address.')
parser.add_argument('--IP', type=str, help='set the IP address of the rPi (server device)')
args = parser.parse_args()

port = 21000
host = str(args.IP) #'192.168.0.100' #socket.gethostname() # Get local machine name

client_socket.connect((host, port) )
connection = client_socket.makefile('wb')

data = b""
payload_size = struct.calcsize(">L")
while True:
    while len(data) < payload_size:
        data += client_socket.recv(4096)

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4096)
        
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    cv2.imshow('ImageWindow',frame)
    cv2.waitKey(1)

client.close()
cv2.destroyAllWindows()
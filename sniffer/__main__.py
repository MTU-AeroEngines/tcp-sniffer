import sys
import socket
from .client import ClientThread

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

LOCAL_BIND_ADDR = '0.0.0.0', int(sys.argv[1])

serverSocket.bind(LOCAL_BIND_ADDR)

serverSocket.listen()

while True:
    (clientConnected, clientAddress) = serverSocket.accept()

    print("Accepted connection request from %s: %s" % (clientAddress[0], clientAddress[1]))
    ClientThread(clientConnected).start()

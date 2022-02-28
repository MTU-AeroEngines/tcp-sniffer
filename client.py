import socket

PORT = 8000
SERVER = '53.158.66.69'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((SERVER, PORT))

while True:
    msg = input("Input data: ")

    client_socket.send(msg.encode())

client_socket.close()
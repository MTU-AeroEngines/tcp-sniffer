import socket
import time

LOCAL_BIND_ADDR = ('127.0.0.1', 8000)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(LOCAL_BIND_ADDR)

for i in range(1, 6):
    data = f"Message number {i}"
    client_socket.sendall(data.encode())
    print(data)
    time.sleep(1)

client_socket.close()


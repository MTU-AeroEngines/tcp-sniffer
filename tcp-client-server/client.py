import socket
import time
import threading
from database import cur

TARGET_SOCK_ADDR = ('127.0.0.1', 65432)

# Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(TARGET_SOCK_ADDR)
except socket.error:
    print("Could not make a connection to the server")


def send_data():
    # Sending data to server
    for i in range(1, 6):
        msg = f"Wiadomosc nr {i} "
        sock.sendall(msg.encode())
        print(msg)
        time.sleep(1)
    # msg = input()
    # sock.sendall(str.encode(msg))

    sock.close()


send_data()

#connections = []
# def handle_sever(conn, addr):
#     global total_connections
#     connections.append(Client(conn, addr, total_connections, True))
#     connections[len(connections) - 1].start()
#     print("New connection at ID " + str(total_connections))
#     total_connections += 1
#
# # Create new thread to wait for data
# receiveThread = threading.Thread(target=receive_data, args=(sock, True))
# receiveThread.start()

import socket
import threading
import logging

logger = logging.getLogger(__name__)

TARGET_SOCK_ADDR = ('127.0.0.1', 8080)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.bind(TARGET_SOCK_ADDR)

clients = []


def send_data():
    threading.Timer(20.0, send_data).start()
    for c in clients:
        data = "Message from server"
        c.sendall(data.encode())


def receive(c):
    while True:
        try:
            data_from_client = c.recv(1024)
            if not data_from_client:
                raise OSError('Socket error!')
            logger.warning('<CLIENT> %s', data_from_client.decode())
        except (socket.error, IOError, OSError):
            logger.warning('[DISCONNECT] Connection closed\n')
            clients.remove(c)
            c.close()
            break


client.listen()

while True:
    conn, addr = client.accept()
    logger.warning('[NEW CONNECTION] Connected with %s', str(addr))

    clients.append(conn)

    receive_thread = threading.Thread(target=receive, args=(conn, ))
    receive_thread.start()

    send_data()

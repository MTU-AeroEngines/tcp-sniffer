import socket
import threading
import logging

logger = logging.getLogger(__name__)

LOCAL_BIND_ADDR = ('127.0.0.1', 8000)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_data():
    try:
        threading.Timer(5.0, send_data).start()
        data = "Message from client"
        server.sendall(data.encode())
    except (socket.error, IOError, OSError):
        logger.warning('[DISCONNECT] Connection closed')
        server.close()
        return


def receive():
    while True:
        try:
            data_from_server = server.recv(1024)
            if not data_from_server:
                raise socket.error('[ERROR] Socket error')
            logger.warning('<SERVER> %s', data_from_server.decode())
        except (socket.error, IOError, OSError):
            logger.warning('[DISCONNECT] Connection closed\n')
            server.close()
            return


server.connect(LOCAL_BIND_ADDR)
logger.warning('[NEW CONNECTION] Connected to the server')

receive_thread = threading.Thread(target=receive)
receive_thread.start()
send_data()





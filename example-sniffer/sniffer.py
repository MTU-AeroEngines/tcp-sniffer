import socket
import threading
import time
import select
import uuid
from database import cur
import logging


logger = logging.getLogger(__name__)
TARGET_SOCK_ADDR = sys.argv[2], int(sys.argv[3])


class ChatServer(threading.Thread):
    # ChatServer class creates new instance for each connected client
    def __init__(self, conn, addr, signal):
        threading.Thread.__init__(self)
        self.facs_socket = conn
        self.address = addr
        self.id = uuid.uuid4().hex
        self.signal = signal
        self.calypso_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def close(self):
        try:
            self.facs_socket.close()
        except (socket.error, IOError, OSError):
            pass
        try:
            self.calypso_socket.close()
        except (socket.error, IOError, OSError):
            pass

    def save_data(self, direction: int, data):
        cur.execute('INSERT INTO data (session_id, timestamp, direction, data) VALUES (?, ?, ?, ?)',
                    (self.id, int(time.time_ns()/1000), direction, data))

    def run(self):
        self.calypso_socket.connect(TARGET_SOCK_ADDR)
        logger.warning('[NEW CONNECTION] New connection %s at ID %s', str(self.address), str(self.id))
        while self.signal:
            try:
                rs, ws, xs = select.select((self.calypso_socket, self.facs_socket), (), ())
                for sock in rs:
                    if sock == self.facs_socket:
                        # Data incoming from the client
                        data = self.facs_socket.recv(1024)
                        logger.warning('<CLIENT> %s', data.decode()))
                        if not data:
                            raise OSError('Socket error!')
                        # 0 -> from the client to the server
                        self.save_data(0, data)
                        self.calypso_socket.sendall(data)
                    else:
                        # Data incoming from the server
                        data = self.calypso_socket.recv(1024)
                        logger.warning('<SERVER> %s', data.decode())
                        if not data:
                            raise OSError('Socket error!')
                        # 1 -> from the server to the client
                        self.save_data(1, data)
                        self.facs_socket.sendall(data)
            except (socket.error, IOError, OSError) as e:
                self.signal = False
                logger.warning('[DISCONNECT] Client %s has been disconnected', str(self.address), exc_info=e)
                self.close()
                break


def main():

    LOCAL_BIND_ADDR = '0.0.0.0', int(sys.argv[1])

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(LOCAL_BIND_ADDR)
    logger.warning('[STARTING] Server is starting...')

    # Enables a server to accept connections
    sock.listen()
    logger.warning('[LISTENING] Server is listening for connection...')

    while True:
        conn, addr = sock.accept()

        # Create new thread to handle the connections
        new_conn_thread = ChatServer(conn, addr, True)
        new_conn_thread.start()


main()


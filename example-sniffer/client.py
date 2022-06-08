import select
import sys
import threading
import socket
import time
import uuid
import logging
from .database import cur

TARGET_SOCK_ADDR = sys.argv[2], int(sys.argv[3])

logger = logging.getLogger(__name__)


DIR_CLIENT_TO_SERVER = 0
DIR_SERVER_TO_CLIENT = 1


class ClientThread(threading.Thread):
    """
    This handles two sockets:

    1. Client socket - self.socket
    """
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.socket = sock      # This is the "client" socket
        self.session_id = uuid.uuid4().hex
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # This is the "server" socket
        self.incoming_socket_fd = sock.fileno()

    def close(self):
        try:
            self.socket.close()
        except (socket.error, IOError, OSError):
            pass
        try:
            self.server_socket.close()
        except (socket.error, IOError, OSError):
            pass

    def run(self):
        self.server_socket.settimeout(10)
        try:
            self.server_socket.connect(TARGET_SOCK_ADDR)
        except (socket.error, OSError, IOError) as e:
            self.close()
            logger.exception('Failed to connect to target', exc_info=e)
            return

        cur.execute('INSERT INTO sessions (session_id) VALUES (?)', (self.session_id, ))
        try:
            while True:
                self.loop()
        except (socket.error, OSError, IOError) as e:
            logger.error('Connection closed', exc_info=e)
            self.close()

    def save_data(self, direction: int, data) -> None:
        cur.execute('INSERT INTO data (session_id, timestamp, direction, data) VALUES (?, ?, ?, ?)',
                    (self.session_id, time.time_ns() // 1000, direction, data))

    def loop(self):
        rs, ws, xs = select.select((self.server_socket, self.socket), (), ())

        for sock in rs:
            if sock.fileno() == self.incoming_socket_fd:
                # We have incoming data on the CLIENT socket
                data = self.socket.recv(1024)
                if not data:
                    raise OSError('Connection closed by the client!')
                self.save_data(DIR_CLIENT_TO_SERVER, data)
                self.server_socket.sendall(data)
            else:
                # We have incoming data on the server socket
                data = self.server_socket.recv(1024)
                if not data:
                    raise OSError('Connection closed by the server!')
                self.save_data(DIR_SERVER_TO_CLIENT, data)
                self.socket.sendall(data)

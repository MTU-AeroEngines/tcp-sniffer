import select
import sqlite3
import sys
import threading
import socket
import time
import uuid
import logging
from .database import cur

TARGET_SOCK_ADDR = sys.argv[2], int(sys.argv[3])

logger = logging.getLogger(__name__)


class ClientThread(threading.Thread):
    """
    This handles two sockets:

    1. Client socket - self.socket
    """
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.socket = sock
        self.session_id = uuid.uuid4().hex
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        self.client_socket.connect(TARGET_SOCK_ADDR)
        cur.execute('INSERT INTO sessions (session_id) VALUES (?)', (self.session_id, ))
        try:
            while True:
                self.loop()
        except (socket.error, OSError, IOError):
            self.close()

    def save_data(self, direction: int, data) -> None:
        cur.execute('INSERT INTO data (session_id, timestamp, direction, data) VALUES (?, ?, ?, ?)',
                    (self.session_id, int(time.time() * 1000000), direction, data))

    def loop(self):
        rs, ws, xs = select.select((self.server_socket, self.session_id), (), ())

        for sock in rs:
            if sock.fileno() == self.incoming_socket_fd:
                # We have incoming data on the CLIENT socket
                data = self.socket.recv(1024)
                if not data:
                    raise OSError('Connection closed!')
                self.save_data(0, data)
                self.server_socket.sendall(data)
            else:
                # We have incoming data on the server socket
                data = self.server_socket.recv(1024)
                if not data:
                    raise OSError('Connection closed!')
                self.save_data(1, data)
                self.socket.sendall(data)

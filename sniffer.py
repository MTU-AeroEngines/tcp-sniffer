import socket
import threading
import time
import select
import uuid
import logging
import sys


import os
import sqlite3

DB_PATH = 'database.db'
db_exists = os.path.exists(DB_PATH)
db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
cur = db.cursor()

if not db_exists:
    cur.execute('''CREATE TABLE data (
                session_id TEXT,
                timestamp UNSIGNED BIGINT,
                direction INT NOT NULL,
                data BLOB NOT NULL,
                PRIMARY KEY (session_id, timestamp)
                )''')



logger = logging.getLogger(__name__)
TARGET_SOCK_ADDR = sys.argv[2], int(sys.argv[3])


class ChatServer(threading.Thread):
    # ChatServer class creates new instance for each connected client
    def __init__(self, conn, addr):
        super().__init__(daemon=True)
        self.client_socket = conn
        self.address = addr
        self.id = uuid.uuid4().hex
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ts = time.monotonic()

    def close(self):
        try:
            self.client_socket.close()
        except (socket.error, IOError, OSError):
            pass
        try:
            self.server_socket.close()
        except (socket.error, IOError, OSError):
            pass

    def save_data(self, direction: int, data):
        cur.execute('INSERT INTO data (session_id, timestamp, direction, data) VALUES (?, ?, ?, ?)',
                    (self.id, time.time_ns(), direction, data))
        db.commit()

    def run(self):
        while True:
            try:
                self.server_socket.connect(TARGET_SOCK_ADDR)
                logger.warning('\n[NEW CONNECTION] New connection %s at ID %s\n', str(self.address), str(self.id))
                break
            except (socket.error, IOError, OSError):
                logger.warning('\n[WAITING] Waiting for the server to connect')
                time.sleep(5)
                if time.monotonic() - self.ts > 120:
                    logger.warning('\n[TIMEOUT] Connection closed. Server has not been connected')
                    self.close()
                    return

        while True:
            try:
                rs, ws, xs = select.select((self.server_socket, self.client_socket), (), ())
                for sock in rs:
                    if sock == self.client_socket:
                        # Data incoming from the client
                        data = self.client_socket.recv(1024)
                        logger.warning('<CLIENT> %s', data.decode())
                        if not data:
                            raise OSError('Connection closed by the client!')
                        # 0 -> from the client to the server
                        self.save_data(0, data)
                        self.server_socket.sendall(data)
                    else:
                        # Data incoming from the server
                        data = self.server_socket.recv(1024)
                        logger.warning('<SERVER> %s', data.decode())
                        if not data:
                            raise OSError('Connection closed by the server!')
                        # 1 -> from the server to the client
                        self.save_data(1, data)
                        self.client_socket.sendall(data)
            except (socket.error, IOError, OSError) as err:
                logger.warning('\n[DISCONNECT] Client %s has been disconnected\n', str(self.address), exc_info=err)
                self.close()
                return


def main():

    LOCAL_BIND_ADDR = '0.0.0.0', int(sys.argv[1])

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(LOCAL_BIND_ADDR)
    logger.warning('\n[STARTING] Server is starting')

    # Enables a server to accept connections
    sock.listen()
    logger.warning('\n[LISTENING] Server is listening for connection')

    while True:
        conn, addr = sock.accept()

        # Create new thread to handle the connections
        new_conn_thread = ChatServer(conn, addr)
        new_conn_thread.start()


main()

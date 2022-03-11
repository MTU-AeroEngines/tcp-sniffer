import sqlite3
import sys
import threading
import socket
from .database import cur

TARGET_SOCK_ADDR = sys.argv[2], int(sys.argv[3])


class ClientThread(threading.Thread):
    def __init__(self, sock):
        super().__init__(daemon=True)
        self.socket = sock
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.client_socket.connect(TARGET_SOCK_ADDR)
        data_no = 1
        while True:
            data_from_client = self.socket.recv(1024)

            print(data_from_client.decode())

            try:
                cur.execute('INSERT INTO obtained_data (data_no, data_value) VALUES (?, ?)',
                            (data_no, data_from_client.decode()))
            except sqlite3.IntegrityError:
                cur.execute('UPDATE obtained_data SET data_from_client.decode()=? WHERE data_no=?',
                            (data_no, data_from_client.decode()))

            data_no += 1


import socket
import sqlite3
import threading
import uuid
import datetime
import os

# ------------------------------DATABASE----------------------------
DB_PATH = 'database.db'

file_exists = os.path.exists(DB_PATH)

db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
if not file_exists:
    cur = db.cursor()
    cur.execute('CREATE TABLE sessions (UUID TEXT)')
    cur.execute('CREATE TABLE CONVERSATIONS ('
                'ID TEXT AUTO_INCREMENT PRIMARY KEY,'
                'msg_1 TEXT,'
                'msg_2 TEXT)')
    cur.close()


class Thread(threading.Thread):
    def __init__(self, sock):
        super().__init__()
        self.socket = sock
        self.cursor = db.cursor()

    def run(self):
        try:
            self._run()
        except Exception as e:
            print('Teardown thanks to', e)
            self.cursor.close()
            self.socket.close()

    def _run(self):
        self.socket.setblocking(True)

        while True:
            data_from_client = self.socket.recv(1024)

            print(data_from_client.decode())

            uuid_no = uuid.uuid4()
            current_time = datetime.datetime.now()
            ID = (uuid_no, current_time)

            try:
                self.cursor.execute('INSERT INTO sessions (UUID) VALUES (?)',
                                    uuid_no)
            except sqlite3.IntegrityError:
                self.cursor.execute('UPDATE sessions SET uuid_no=? WHERE uuid_no=?',
                                    uuid_no)
            try:
                self.cursor.execute('INSERT INTO CONVERSATIONS (ID, msg_1, msg_2) VALUES (?, ?, ?)',
                                    (ID, data_from_client, data_from_client))
            except sqlite3.IntegrityError:
                self.cursor.execute('UPDATE CONVERSATIONS SET uuid_no=? WHERE uuid_no=?',
                                    uuid_no)


# ------------------------------SERVER------------------------------

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

PORT = 8000
SERVER = '53.158.66.69'

serverSocket.bind((SERVER, PORT))

serverSocket.listen()

while True:
    (clientConnected, clientAddress) = serverSocket.accept()
    Thread(clientConnected).start()

    print("Accepted connection request from %s: %s" % (clientAddress[0], clientAddress[1]))

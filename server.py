import socket
import sqlite3
import threading
import uuid

# ------------------------------DATABASE----------------------------
DB_PATH = 'database.db'

file_exists = os.path.exists(DB_PATH)

db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
if not file_exists:
    cur = db.cursor()
    cur.execute('CREATE TABLE obtained_data ('
                'data_no TEXT,'
                'data_value TEXT)')
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

        data_no = 1
        while True:
            data_from_client = self.socket.recv(1024)

            print(data_from_client.decode())

            try:
                self.cursor.execute('INSERT INTO obtained_data (data_no, data_value) VALUES (?, ?)',
                                    (data_no, data_from_client.decode()))
            except sqlite3.IntegrityError:
                self.cursor.execute('UPDATE obtained_data SET data_from_client.decode()=? WHERE data_no=?',
                                    (data_no, data_from_client.decode()))

            data_no += 1


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

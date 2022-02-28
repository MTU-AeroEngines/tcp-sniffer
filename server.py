import socket
import sqlite3

# ------------------------------DATABASE----------------------------
DB_PATH = 'database.db'

db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
cur = db.cursor()
cur.execute('CREATE TABLE obtained_data ('
            'data_no TEXT,'
            'data_value TEXT)')

# ------------------------------SERVER------------------------------

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

PORT = 8000
SERVER = '53.158.66.69'

serverSocket.bind((SERVER, PORT))

serverSocket.listen()

while True:
    (clientConnected, clientAddress) = serverSocket.accept()

    print("Accepted connection request from %s: %s" % (clientAddress[0], clientAddress[1]))

    data_no = 1
    while True:
        data_from_client = clientConnected.recv(1024)

        print(data_from_client.decode())

        try:
            cur.execute('INSERT INTO obtained_data (data_no, data_value) VALUES (?, ?)',
                        (data_no, data_from_client.decode()))
        except sqlite3.IntegrityError:
            cur.execute('UPDATE obtained_data SET data_from_client.decode()=? WHERE data_no=?',
                        (data_no, data_from_client.decode()))

        data_no += 1

import socket
import threading
import time
import select
import uuid
from database import cur

TARGET_SOCK_ADDR = ('127.0.0.1', 8080)


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
                    (self.id, int(time.time()*1000000), direction, data))

    def run(self):
        self.calypso_socket.connect(TARGET_SOCK_ADDR)
        print("New connection " + str(TARGET_SOCK_ADDR) + " at ID " + str(self.id))
        while self.signal:
            try:
                rs, ws, xs = select.select((self.calypso_socket, self.facs_socket), (), ())
                for sock in rs:
                    if sock == self.facs_socket:
                        # Data incoming from the client
                        data = self.facs_socket.recv(1024)
                        if not data:
                            raise OSError('Socket error!')
                        # 0 -> from the client to the server
                        self.save_data(0, data)
                        self.calypso_socket.sendall(data)
                    else:
                        # Data incoming from the server
                        data = self.calypso_socket.recv(1024)
                        if not data:
                            raise OSError('Socket error!')
                        # 1 -> from the server to the client
                        self.save_data(1, data)
                        self.facs_socket.sendall(data)
            except (socket.error, IOError, OSError):
                self.signal = False
                print("Client " + str(TARGET_SOCK_ADDR) + " has disconnected\n")
                self.close()
                break


def main():

    LOCAL_BIND_ADDR = ('127.0.0.1', 8000)

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(LOCAL_BIND_ADDR)
    print("Server is starting...")

    # Enables a server to accept connections
    sock.listen()

    while True:
        conn, addr = sock.accept()
        print(f"Accepted connection request from ({addr[0]}, {addr[1]})")

        # Create new thread to handle the connections
        new_conn_thread = ChatServer(conn, addr, True)
        new_conn_thread.start()


main()


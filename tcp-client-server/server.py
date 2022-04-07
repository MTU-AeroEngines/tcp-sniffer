import socket
import threading
import time
from database import cur

connections = []
total_connections = 1


class Client(threading.Thread):
    # Client class, new instance created for each connected client
    def __init__(self, socket, address, id, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.signal = signal

    def close(self):
        try:
            self.socket.close()
        except socket.error:
            pass

    def save_data(self, direction: int, data):
        cur.execute('INSERT INTO data (session_id, timestamp, direction, data) VALUES (?, ?, ?, ?)',
                    (self.id, int(time.time()*1000000), direction, data))

    # Attempt to get data from client
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
            except socket.error:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                self.close()
                break
            self.save_data(1, data)
            self.socket.sendall(data)
            print(str(data.decode()))


def handle_conn(conn, addr):
    global total_connections
    connections.append(Client(conn, addr, total_connections, True))
    connections[len(connections) - 1].start()
    print("New connection " + str(addr) + " at ID " + str(total_connections))
    total_connections += 1
    

def main():
    TARGET_SOCK_ADDR = ('127.0.0.1', 65432)

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(TARGET_SOCK_ADDR)
    print("Server is starting...")

    # Enables a server to accept connections
    sock.listen()
    print("Server is listening...")

    while True:
        conn, addr = sock.accept()

        # Create new thread to wait for connections
        new_conn_thread = threading.Thread(target=handle_conn, args=(conn, addr))
        new_conn_thread.start()


main()

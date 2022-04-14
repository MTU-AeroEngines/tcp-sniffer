import socket

TARGET_SOCK_ADDR = ('127.0.0.1', 8080)

calypso_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
calypso_socket.bind(TARGET_SOCK_ADDR)
calypso_socket.listen()

while True:
    conn, addr = calypso_socket.accept()

    try:
        while True:
            data_from_client = conn.recv(1024)
            if not data_from_client:
                break
            conn.sendall(data_from_client)
            print(data_from_client.decode())
    except socket.error:
        conn.close()

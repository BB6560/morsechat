import socket
import threading

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5000
clients = set()
lock = threading.Lock()

def handle_client(client_socket):
    global clients
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            with lock:
                for client in clients:
                    if client != client_socket:
                        client.sendall(data.encode())
        except:
            break
    with lock:
        clients.remove(client_socket)
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        with lock:
            clients.add(client_socket)
        print(f"Client connected: {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()

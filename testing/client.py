import socket
import threading
import keyboard  # `pip install keyboard`

SERVER_IP = "127.0.0.1"  # Change this to your server's IP
PORT = 5000

def listen_for_server_messages(client_socket):
    """Listen for messages from the server to control the beep."""
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            if data == "PRESSED":
                print("ON")
            elif data == "RELEASED":
                print("OFF")
    except (ConnectionResetError, ConnectionAbortedError):
        print("Server disconnected.")
    finally:
        client_socket.close()

def start_client():
    """Start the client and send the key press/release status to the server."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_IP, PORT))
        threading.Thread(target=listen_for_server_messages, args=(client,), daemon=True).start()

        while True:
            keyboard.wait("space")  # Wait for space key press
            try:
                client.sendall("PRESSED".encode())  # Send "PRESSED" to server
                print("Press sent")
            except OSError:
                print("Connection lost.")
                break  # Exit loop if the connection is closed

            keyboard.wait("space", suppress=True, trigger_on_release=True)  # Wait for space release
            try:
                client.sendall("RELEASED".encode())  # Send "RELEASED" to server
                print("Release sent")
            except OSError:
                print("Connection lost.")
                break  # Exit loop if the connection is closed

    except ConnectionRefusedError:
        print("Could not connect to the server.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    start_client()

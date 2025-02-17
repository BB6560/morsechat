import argparse

#args
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--set-device', type=int, help='Specify output device with ID from device list', metavar='<id>')
parser.add_argument('-ld', '--list-devices', action='store_true', help='Lists output devices', dest='listdevices')
args = parser.parse_args()

import sounddevice as sd
if args.listdevices:
    available_devices = sd.query_devices()
    print(available_devices)
    exit()

import socket
import threading
import keyboard  # `pip install keyboard`
import numpy as np
import sys

# Parameters for Beeping Sound
frequency = 800  # Frequency in Hz
sample_rate = 44100  # Sample rate (samples per second)
volume = 0.2  # Initial volume (0.0 to 1.0)

# Socket parameters for client
SERVER_IP = "127.0.0.1"  # Change this to your server's IP
PORT = 5000

# A flag for the audio playback thread to stop when needed
stop_flag = threading.Event()

def generate_sine_wave_chunk(frequency, sample_rate, volume, chunk_size=1024):
    """Generates a chunk of a sine wave signal."""
    t = np.linspace(0, chunk_size / sample_rate, chunk_size, endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t) * volume
    return wave.astype(np.float32)

def audio_callback(outdata, frames, time, status):
    """Callback to continuously generate the sine wave and play it."""
    global volume
    if status:
        print(status, file=sys.stderr)

    # Generate the sine wave for the current chunk
    sine_wave = generate_sine_wave_chunk(frequency, sample_rate, volume, chunk_size=frames)

    # Reshape the generated wave to match the expected shape (frames, 1 channel)
    outdata[:] = sine_wave.reshape(-1, 1)

def listen_for_server_messages(client_socket):
    """Listen for messages from the server to control the beep."""
    global volume
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            if data == "PRESSED":
                print("ON")
                volume = 1.0  # Set volume to 1 when "PRESSED"
            elif data == "RELEASED":
                print("OFF")
                volume = 0.0  # Set volume to 0 when "RELEASED"
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

# Start the client thread
thread = threading.Thread(target=start_client, daemon=True)
thread.start()

output_device = 11
if args.device:
    output_device = args.device
    print(f"Output device set to {output_device}")    

# Start the audio stream with a callback for real-time audio generation
stream = sd.OutputStream(
    samplerate=sample_rate,
    channels=1,
    dtype=np.float32,
    callback=audio_callback,
    device=output_device,
    blocksize=2048  # Use 'blocksize' instead of 'frames_per_buffer'
)



# Open the audio stream
stream.start()

# Keep the main program running
try:
    while True:
        pass
except KeyboardInterrupt:
    # Stop the audio stream and the client when exiting
    stop_flag.set()
    stream.stop()
    print("Stream stopped.")

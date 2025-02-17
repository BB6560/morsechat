import numpy as np
import sounddevice as sd
import threading
import sys

# Parameters
frequency = 800  # Frequency in Hz
sample_rate = 44100  # Sample rate (samples per second)
volume = 0.5  # Initial volume (0.0 to 1.0)

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

def volume_control_thread():
    """Thread for adjusting volume in real-time."""
    global volume
    while not stop_flag.is_set():
        try:
            new_volume = float(input("Enter volume (0.0 to 1.0): "))
            if 0.0 <= new_volume <= 1.0:
                volume = new_volume
            else:
                print("Invalid volume, please enter a value between 0.0 and 1.0.")
        except ValueError:
            print("Invalid input, please enter a number.")

# Start the volume control thread
thread = threading.Thread(target=volume_control_thread, daemon=True)
thread.start()

# Find available output devices
print("Available output devices:")
print(sd.query_devices())

# Set the output device (uncomment and modify if necessary)
output_device = 2  # Set to None for default, or specify device index if needed
# output_device = 1  # Example: Set to a specific device index

# Open the audio stream with a callback for real-time audio generation
stream = sd.OutputStream(
    samplerate=sample_rate,
    channels=1,
    dtype=np.float32,
    callback=audio_callback,
    device=output_device  # Explicitly set the output device
)

# Start the audio stream
stream.start()

# Keep the main program running
try:
    while True:
        pass
except KeyboardInterrupt:
    # Stop the audio stream and volume control when exiting
    stop_flag.set()
    stream.stop()
    print("Stream stopped.")

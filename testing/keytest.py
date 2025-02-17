import keyboard

while True:
    keyboard.wait("space")  # Wait for space key press
    print("on")
    keyboard.wait("space", suppress=True, trigger_on_release=True)  # Wait for space release
    print("off")
import serial
import time

# Your Arduino's port (adjust this!)
PORT = 'COM4'  # or '/dev/ttyUSB0' on Linux
BAUD = 9600

# Example learned directions
directions = ['RIGHT', 'RIGHT', 'DOWN', 'DOWN']

def send_path_to_arduino(directions):
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        time.sleep(2)  # wait for Arduino to reset
        for direction in directions:
            print(f"Sending: {direction}")
            ser.write((direction + '\n').encode())
            time.sleep(0.5)  # give Arduino time to act

if __name__ == "__main__":
    send_path_to_arduino(directions)

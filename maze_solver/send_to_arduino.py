# send_to_arduino.py

import argparse
import os
import sys
import time

from maze_env import path_to_directions

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Your Arduino's port (adjust this, or pass --port)
PORT = 'COM4'  # or '/dev/ttyUSB0' on Linux
BAUD = 9600
MOVE_TIMEOUT = 15  # seconds to wait for the robot to finish one move


def load_path(filename):
    path = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                x, y = line.split(",")
                path.append((int(x), int(y)))
    return path


def wait_for_reply(ser, timeout):
    """Read lines from the Arduino until it answers OK / BLOCKED / ERR."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = ser.readline().decode(errors="replace").strip()
        if not line:
            continue
        print(f"  Arduino: {line}")
        if line.startswith(("OK", "BLOCKED", "ERR")):
            return line
    return None


class RobotError(Exception):
    pass


def send_path_to_arduino(directions, port=PORT, baud=BAUD, ser=None):
    """Send directions one at a time, waiting for the robot to finish each.
    Pass ser to use an already-open connection (e.g. robot_sim.FakeSerial)."""
    if ser is None:
        import serial  # imported here so --dry-run works without pyserial
        ser = serial.Serial(port, baud, timeout=1)

    with ser:
        # Opening the port resets the Arduino; wait for its READY message
        print("Waiting for Arduino...")
        deadline = time.time() + 5
        while time.time() < deadline:
            if ser.readline().decode(errors="replace").strip() == "READY":
                break
        ser.reset_input_buffer()

        # Tell the robot it is back at the start, facing its starting direction
        ser.write(b"RESET\n")
        if wait_for_reply(ser, 5) is None:
            raise RobotError("No reply from the Arduino. Is pathmind_robot.ino uploaded and the port correct?")

        for i, direction in enumerate(directions, 1):
            print(f"[{i}/{len(directions)}] Sending: {direction}")
            ser.write((direction + '\n').encode())
            reply = wait_for_reply(ser, MOVE_TIMEOUT)
            if reply is None:
                raise RobotError("Timed out waiting for the robot to finish the move.")
            if reply.startswith("BLOCKED"):
                raise RobotError(f"Robot saw a wall ahead on move {i} ({direction}) and stopped. "
                                 "Check its position and calibration.")
            if reply.startswith("ERR"):
                raise RobotError(f"Robot rejected the command: {reply}")

        print("Path complete!")


def main():
    parser = argparse.ArgumentParser(description="Send the learned path to the PathMind robot.")
    parser.add_argument("--port", default=PORT, help=f"serial port (default {PORT})")
    parser.add_argument("--baud", type=int, default=BAUD)
    parser.add_argument("--path", default=os.path.join(ROOT, "learned_path.txt"),
                        help="path file written by main.py")
    parser.add_argument("--dry-run", action="store_true", help="print the directions without sending them")
    parser.add_argument("--print-array", action="store_true",
                        help="print the path as a C array to paste into pathmind_robot.ino")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        sys.exit(f"{args.path} not found. Run main.py first to train a path.")

    directions = path_to_directions(load_path(args.path))
    print("Directions:", ", ".join(directions))

    if args.print_array:
        items = ", ".join(f'"{d}"' for d in directions)
        print(f"\nconst char* path[] = {{{items}}};")
        return
    if args.dry_run:
        return

    try:
        send_path_to_arduino(directions, args.port, args.baud)
    except RobotError as e:
        sys.exit(str(e))
    except ImportError:
        sys.exit("pyserial is not installed. Run: pip install -r requirements.txt")
    except OSError as e:
        from serial.tools import list_ports
        ports = ", ".join(p.device for p in list_ports.comports()) or "none found"
        sys.exit(f"Couldn't open {args.port}: {e}\nAvailable ports: {ports}")


if __name__ == "__main__":
    main()

# robot_sim.py
#
# A software stand-in for arduino/pathmind_robot/pathmind_robot.ino. It speaks
# the same serial protocol and uses the same turn logic as the sketch, so
# send_to_arduino.py can be tested without hardware. If you change how the
# sketch moves or replies, update this file to match.

import math

HEADINGS = ["UP", "RIGHT", "DOWN", "LEFT"]  # clockwise, same order as the sketch
SENSOR_AHEAD = 0.3   # distance from the robot's centre to its centre sensor, in cells
DRIVE_FRAMES = 12    # animation frames per cell driven
TURN_FRAMES = 8      # animation frames per 90 degree turn


def heading_angle(heading):
    """Angle in degrees on the maze drawing: RIGHT = 0, UP = 90, DOWN = -90."""
    return 90 - 90 * heading


class SimRobot:
    """A robot that drives on the maze grid by dead reckoning, like the real one.

    turn_error and drive_error are fractions (0.1 = turns 10% too far), for
    seeing what a badly calibrated turnTimeMs / cellTimeMs does.
    """

    def __init__(self, maze, start, start_heading="DOWN", turn_error=0.0, drive_error=0.0):
        self.maze = maze
        self.start = start
        self.start_heading = HEADINGS.index(start_heading)
        self.turn_error = turn_error
        self.drive_error = drive_error
        self.frames = []  # (row, col, angle, label) snapshots, for animation
        self.blocked = False
        self._place_at_start()

    def _place_at_start(self):
        self.heading = self.start_heading  # which way the robot *thinks* it faces
        self.row, self.col = float(self.start[0]), float(self.start[1])
        self.angle = heading_angle(self.start_heading)  # which way it really faces
        self._snapshot("At start, facing " + HEADINGS[self.start_heading])

    @property
    def cell(self):
        return (math.floor(self.row + 0.5), math.floor(self.col + 0.5))

    def handle(self, cmd):
        """Process one serial command. Returns the lines the robot prints back."""
        cmd = cmd.strip().upper()
        if not cmd:
            return []
        replies = [f"Received: {cmd}"]
        if cmd == "RESET":
            self._place_at_start()
            replies.append("OK")
        elif cmd == "SENSE":
            replies.append("Sensors (simulated): centre sees " + ("black" if self.sensor_on_wall() else "white"))
            replies.append("OK")
        elif cmd in HEADINGS:
            replies.append("OK" if self.follow_direction(cmd) else "BLOCKED")
        else:
            replies.append("ERR unknown command")
        return replies

    def follow_direction(self, direction):
        target = HEADINGS.index(direction)
        turns = (target - self.heading) % 4  # 0 = straight, 1 = right, 2 = around, 3 = left
        if turns == 1:
            self._turn(-90, f"{direction}: turning right")
        elif turns == 2:
            self._turn(-90, f"{direction}: turning around")
            self._turn(-90, f"{direction}: turning around")
        elif turns == 3:
            self._turn(90, f"{direction}: turning left")
        self.heading = target
        return self._drive_one_cell(f"{direction}: driving forward")

    def _turn(self, degrees, label):
        step = degrees * (1 + self.turn_error) / TURN_FRAMES
        for _ in range(TURN_FRAMES):
            self.angle += step
            self._snapshot(label)

    def _drive_one_cell(self, label):
        step = (1 + self.drive_error) / DRIVE_FRAMES
        rad = math.radians(self.angle)
        for _ in range(DRIVE_FRAMES):
            self.col += math.cos(rad) * step
            self.row -= math.sin(rad) * step
            if self.sensor_on_wall():
                self.blocked = True
                self._snapshot("BLOCKED: sensor sees a wall")
                return False
            self._snapshot(label)
        return True

    def sensor_position(self):
        rad = math.radians(self.angle)
        return self.row - math.sin(rad) * SENSOR_AHEAD, self.col + math.cos(rad) * SENSOR_AHEAD

    def sensor_on_wall(self):
        r, c = self.sensor_position()
        r, c = math.floor(r + 0.5), math.floor(c + 0.5)
        if not (0 <= r < len(self.maze) and 0 <= c < len(self.maze[0])):
            return True  # off the edge of the maze counts as black
        return self.maze[r][c] == 1

    def _snapshot(self, label):
        self.frames.append((self.row, self.col, self.angle, label))


class FakeSerial:
    """Just enough of serial.Serial for send_to_arduino.py to talk to a SimRobot."""

    def __init__(self, robot):
        self.robot = robot
        self._lines = ["PathMind starting...", "READY"]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def write(self, data):
        for cmd in data.decode().splitlines():
            self._lines += self.robot.handle(cmd)

    def readline(self):
        return (self._lines.pop(0) + "\r\n").encode() if self._lines else b""

    def reset_input_buffer(self):
        self._lines.clear()

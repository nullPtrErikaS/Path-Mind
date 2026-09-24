# simulate.py
#
# Run the whole pipeline without hardware: the learned path is sent through
# send_to_arduino.py to a simulated robot (robot_sim.py), and the robot's drive
# is animated.

import argparse
import math
import os
import re
import sys

from maze_env import MazeEnv, load_maze, path_to_directions
from q_learning import train, greedy_path
from robot_sim import HEADINGS, FakeSerial, SimRobot
from send_to_arduino import RobotError, load_path, send_path_to_arduino

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKETCH = os.path.join(ROOT, "arduino", "pathmind_robot", "pathmind_robot.ino")


def sketch_start_heading():
    """Read START_HEADING from the Arduino sketch so the simulation matches it."""
    try:
        with open(SKETCH) as f:
            match = re.search(r"START_HEADING\s*=\s*HEADING_(\w+)", f.read())
        if match and match.group(1) in HEADINGS:
            return match.group(1)
    except OSError:
        pass
    return "DOWN"


def path_fits_maze(path, maze, start, goal):
    if not path or path[0] != start or path[-1] != goal:
        return False
    for x, y in path:
        if not (0 <= x < len(maze) and 0 <= y < len(maze[0])) or maze[x][y] == 1:
            return False
    try:
        path_to_directions(path)
    except ValueError:
        return False
    return True


def get_path(args, maze, start, goal):
    """Use a saved path if it matches this maze, otherwise train a new one."""
    path_file = args.path or os.path.join(ROOT, "learned_path.txt")
    if os.path.exists(path_file):
        path = load_path(path_file)
        if path_fits_maze(path, maze, start, goal):
            print(f"Using saved path from {path_file}")
            return path
        if args.path:
            sys.exit(f"{path_file} doesn't fit {args.maze} (wrong start/goal or goes through a wall).")
        print(f"{path_file} is for a different maze, so training a new path.")

    print("Training...")
    env = MazeEnv(maze, start, goal)
    path = greedy_path(env, train(env, episodes=args.episodes, verbose=False))
    if path is None:
        sys.exit("The agent couldn't learn a path. Try more --episodes, or check the maze is solvable.")
    return path


def robot_outline(row, col, angle, size=0.32):
    """Arrow-shaped robot outline in plot coordinates (x = col, y = row)."""
    rad = math.radians(angle)
    fwd = (math.cos(rad), -math.sin(rad))    # y points down the drawing
    left = (-math.sin(rad), -math.cos(rad))
    shape = [(1.1, 0), (-0.8, 0.8), (-0.4, 0), (-0.8, -0.8)]
    return [(col + size * (u * fwd[0] + v * left[0]), row + size * (u * fwd[1] + v * left[1]))
            for u, v in shape]


def animate(robot, maze, start, goal, title, speed=1.0, save_to=None, show=True):
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.patches import Polygon
    from plot_path import draw_maze

    frames = robot.frames + [robot.frames[-1]] * 30  # hold on the last frame

    fig, ax = plt.subplots(figsize=(7, 6))
    draw_maze(ax, maze, start, goal)
    ax.set_title(title)
    trail, = ax.plot([], [], color="tab:blue", linewidth=3, alpha=0.5)
    body = Polygon(robot_outline(*frames[0][:3]), closed=True, facecolor="tab:orange",
                   edgecolor="black", zorder=5)
    ax.add_patch(body)
    sensor, = ax.plot([], [], "o", markersize=6, markeredgecolor="black", zorder=6)
    status = fig.text(0.05, 0.03, "", fontsize=11, family="monospace")
    fig.tight_layout(rect=(0, 0.06, 1, 1))

    def update(i):
        row, col, angle, label = frames[i]
        body.set_xy(robot_outline(row, col, angle))
        trail.set_data([f[1] for f in frames[:i + 1]], [f[0] for f in frames[:i + 1]])

        rad = math.radians(angle)
        sr, sc = row - math.sin(rad) * 0.3, col + math.cos(rad) * 0.3
        sensor.set_data([sc], [sr])
        on_black = label.startswith("BLOCKED")
        sensor.set_markerfacecolor("red" if on_black else "lime")
        status.set_text(label)
        status.set_color("red" if on_black else "black")
        return body, trail, sensor, status

    anim = FuncAnimation(fig, update, frames=len(frames), interval=40 / speed, repeat=False)
    if save_to:
        print(f"Saving animation to {save_to} ...")
        anim.save(save_to, writer=PillowWriter(fps=int(25 * speed)))
    if show:
        plt.show()
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Simulate the PathMind robot driving the learned path.")
    parser.add_argument("--maze", default=os.path.join(ROOT, "maze.txt"))
    parser.add_argument("--path", help="path file to drive (default: learned_path.txt, or train a new one)")
    parser.add_argument("--episodes", type=int, default=1000, help="training episodes if a path is needed")
    parser.add_argument("--start-heading", choices=HEADINGS, default=sketch_start_heading(),
                        help="which way the robot faces at the start (default: START_HEADING from the sketch)")
    parser.add_argument("--turn-error", type=float, default=0, metavar="PCT",
                        help="make every turn this many percent too far (negative = too short)")
    parser.add_argument("--drive-error", type=float, default=0, metavar="PCT",
                        help="make every forward move this many percent too long (negative = too short)")
    parser.add_argument("--speed", type=float, default=1.0, help="animation speed multiplier")
    parser.add_argument("--save-gif", metavar="GIF", help="save the animation as a GIF")
    parser.add_argument("--no-show", action="store_true", help="don't open the animation window")
    args = parser.parse_args()

    maze, start, goal = load_maze(args.maze)
    path = get_path(args, maze, start, goal)
    directions = path_to_directions(path)
    print("Directions:", ", ".join(directions))
    print(f"Robot starts facing {args.start_heading}\n")

    robot = SimRobot(maze, start, args.start_heading,
                     turn_error=args.turn_error / 100, drive_error=args.drive_error / 100)
    try:
        send_path_to_arduino(directions, ser=FakeSerial(robot))
    except RobotError as e:
        print(e)

    if robot.cell == goal and not robot.blocked:
        title = f"Simulation: reached the goal in {len(directions)} moves"
    else:
        title = f"Simulation: stopped at {robot.cell}, goal is {goal}"
    print("\n" + title)

    if args.save_gif or not args.no_show:
        animate(robot, maze, start, goal, title, speed=args.speed,
                save_to=args.save_gif, show=not args.no_show)


if __name__ == "__main__":
    main()

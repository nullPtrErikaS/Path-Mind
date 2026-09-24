# maze_env.py

import numpy as np

# Actions, as (row, col) offsets. Row 0 is the top of the maze.
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
ACTIONS = [UP, DOWN, LEFT, RIGHT]
ACTION_NAMES = ["UP", "DOWN", "LEFT", "RIGHT"]
MOVES = {UP: (-1, 0), DOWN: (1, 0), LEFT: (0, -1), RIGHT: (0, 1)}

WALL_CHARS = "#1"
OPEN_CHARS = ".0SG"


def load_maze(path):
    """Read a maze file. Returns (maze, start, goal).

    maze is a list of rows of 0 (open) / 1 (wall). Comment lines start with
    "# " (a hash followed by a space) and blank lines are skipped.
    """
    maze, start, goal = [], None, None
    with open(path) as f:
        for line in f:
            line = line.rstrip()
            if not line or line.startswith("# "):
                continue
            row = []
            for col, ch in enumerate(line):
                if ch in WALL_CHARS:
                    row.append(1)
                elif ch in OPEN_CHARS:
                    row.append(0)
                else:
                    raise ValueError(f"{path}: unexpected character {ch!r} in row {len(maze)}")
                if ch == "S":
                    start = (len(maze), col)
                elif ch == "G":
                    goal = (len(maze), col)
            maze.append(row)

    if not maze:
        raise ValueError(f"{path}: maze is empty")
    if any(len(row) != len(maze[0]) for row in maze):
        raise ValueError(f"{path}: all maze rows must be the same length")
    if start is None or goal is None:
        raise ValueError(f"{path}: maze needs one 'S' (start) and one 'G' (goal)")
    return maze, start, goal


def path_to_directions(path):
    """Convert a list of (row, col) cells into direction names like 'RIGHT'."""
    directions = []
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        delta = (r2 - r1, c2 - c1)
        for action, move in MOVES.items():
            if move == delta:
                directions.append(ACTION_NAMES[action])
                break
        else:
            raise ValueError(f"cells {(r1, c1)} and {(r2, c2)} are not neighbours")
    return directions


class MazeEnv:
    def __init__(self, maze, start, goal, wall_penalty=-5):
        self.maze = np.array(maze)
        self.start = start
        self.goal = goal
        self.wall_penalty = wall_penalty
        self.reset()

    @property
    def n_states(self):
        return self.maze.size

    def reset(self):
        self.agent_pos = self.start
        return self.agent_pos

    def step(self, action):
        dx, dy = MOVES[action]
        x, y = self.agent_pos[0] + dx, self.agent_pos[1] + dy

        reward = -1
        if (0 <= x < self.maze.shape[0] and
            0 <= y < self.maze.shape[1] and
            self.maze[x, y] != 1):
            self.agent_pos = (x, y)
        else:
            reward = self.wall_penalty  # bumped into a wall or the edge

        done = False
        if self.agent_pos == self.goal:
            reward = 100
            done = True

        return self.agent_pos, reward, done

    def render(self):
        maze_copy = self.maze.copy()
        x, y = self.agent_pos
        maze_copy[x, y] = 2
        print(maze_copy)

import contextlib
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "maze_solver"))

from maze_env import MazeEnv, load_maze, path_to_directions, UP, RIGHT  # noqa: E402
from q_learning import train, greedy_path  # noqa: E402


def write_maze(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write(text)
    f.close()
    return f.name


class LoadMazeTest(unittest.TestCase):
    def test_loads_default_maze(self):
        maze, start, goal = load_maze(os.path.join(ROOT, "maze.txt"))
        self.assertEqual(len(maze), 5)
        self.assertEqual(start, (0, 0))
        self.assertEqual(goal, (4, 4))
        self.assertEqual(maze[0], [0, 1, 0, 0, 0])

    def test_accepts_digits_and_skips_comments(self):
        name = write_maze("# comment\n\nS1\n0G\n")
        maze, start, goal = load_maze(name)
        os.remove(name)
        self.assertEqual(maze, [[0, 1], [0, 0]])
        self.assertEqual((start, goal), ((0, 0), (1, 1)))

    def test_rejects_missing_goal(self):
        name = write_maze("S.\n..\n")
        with self.assertRaises(ValueError):
            load_maze(name)
        os.remove(name)


class EnvTest(unittest.TestCase):
    def test_wall_blocks_and_penalises(self):
        env = MazeEnv([[0, 1], [0, 0]], (0, 0), (1, 1))
        state, reward, done = env.step(RIGHT)
        self.assertEqual(state, (0, 0))
        self.assertEqual(reward, env.wall_penalty)
        state, reward, done = env.step(UP)  # off the edge
        self.assertEqual(state, (0, 0))
        self.assertFalse(done)


class DirectionsTest(unittest.TestCase):
    def test_path_to_directions(self):
        path = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        self.assertEqual(path_to_directions(path), ["DOWN", "RIGHT", "UP", "LEFT"])

    def test_rejects_jumps(self):
        with self.assertRaises(ValueError):
            path_to_directions([(0, 0), (2, 0)])


class TrainingTest(unittest.TestCase):
    def test_learns_shortest_path_on_default_maze(self):
        maze, start, goal = load_maze(os.path.join(ROOT, "maze.txt"))
        env = MazeEnv(maze, start, goal)
        q_table = train(env, episodes=1000, seed=0, verbose=False)
        path = greedy_path(env, q_table)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        self.assertEqual(len(path) - 1, 8)  # shortest route through this maze
        for x, y in path:
            self.assertEqual(maze[x][y], 0, "path goes through a wall")


class SimulationTest(unittest.TestCase):
    DIRECTIONS = ["DOWN", "DOWN", "RIGHT", "RIGHT", "DOWN", "DOWN", "RIGHT", "RIGHT"]

    def run_robot(self, **kwargs):
        from robot_sim import FakeSerial, SimRobot
        from send_to_arduino import send_path_to_arduino
        maze, start, goal = load_maze(os.path.join(ROOT, "maze.txt"))
        robot = SimRobot(maze, start, **kwargs)
        with open(os.devnull, "w") as quiet, contextlib.redirect_stdout(quiet):
            send_path_to_arduino(self.DIRECTIONS, ser=FakeSerial(robot))
        return robot, goal

    def test_calibrated_robot_reaches_goal(self):
        for heading in ["UP", "DOWN", "LEFT", "RIGHT"]:
            robot, goal = self.run_robot(start_heading=heading)
            self.assertEqual(robot.cell, goal)
            self.assertFalse(robot.blocked)

    def test_bad_turns_get_blocked_by_wall_sensor(self):
        from send_to_arduino import RobotError
        with self.assertRaises(RobotError):
            self.run_robot(start_heading="DOWN", turn_error=0.3)


if __name__ == "__main__":
    unittest.main()

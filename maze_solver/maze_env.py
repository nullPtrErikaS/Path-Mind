# maze_env.py

import numpy as np

class MazeEnv:
    def __init__(self, maze, start, goal):
        self.maze = np.array(maze)
        self.start = start
        self.goal = goal
        self.reset()

    def reset(self):
        self.agent_pos = self.start
        return self.agent_pos

    def step(self, action):
        x, y = self.agent_pos
        if action == 0:  # UP
            x -= 1
        elif action == 1:  # DOWN
            x += 1
        elif action == 2:  # LEFT
            y -= 1
        elif action == 3:  # RIGHT
            y += 1

        if (0 <= x < self.maze.shape[0] and
            0 <= y < self.maze.shape[1] and
            self.maze[x, y] != 1):
            self.agent_pos = (x, y)

        reward = -1
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

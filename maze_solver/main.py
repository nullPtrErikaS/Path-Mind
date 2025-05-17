# main.py

import numpy as np
import random
from maze_env import MazeEnv

from plot_path import plot_maze_with_path

# Maze map
maze = [
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0],
]
start = (0, 0)
goal = (4, 4)

env = MazeEnv(maze, start, goal)
actions = [0, 1, 2, 3]  # UP, DOWN, LEFT, RIGHT

# Q-table setup
q_table = {}
alpha = 0.1
gamma = 0.9
epsilon = 0.2
episodes = 1000

# Initialize Q-values
for x in range(len(maze)):
    for y in range(len(maze[0])):
        q_table[(x, y)] = [0 for _ in range(len(actions))]

for episode in range(episodes):
    state = env.reset()
    done = False

    while not done:
        if random.uniform(0, 1) < epsilon:
            action = random.choice(actions)
        else:
            action = np.argmax(q_table[state])

        next_state, reward, done = env.step(action)

        old_value = q_table[state][action]
        next_max = max(q_table[next_state])

        new_value = old_value + alpha * (reward + gamma * next_max - old_value)
        q_table[state][action] = new_value

        state = next_state

    if episode % 100 == 0:
        print(f"Episode {episode} done")

print("\nTraining complete. Learned path from start:")
env.reset()
done = False
path = []
while not done:
    state = env.agent_pos
    action = np.argmax(q_table[state])
    path.append(state)
    _, _, done = env.step(action)

path.append(goal)
print(path)

plot_maze_with_path(maze, path, start, goal)

# Save path to file for Arduino or future use
with open("learned_path.txt", "w") as f:
    for x, y in path:
        f.write(f"{x},{y}\n")
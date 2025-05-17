# plot_path.py

import matplotlib.pyplot as plt
import numpy as np

def plot_maze_with_path(maze, path, start, goal):
    maze = np.array(maze)
    display = np.copy(maze)

    for x, y in path:
        display[x, y] = 0.5  # Path cells in gray

    sx, sy = start
    gx, gy = goal
    display[sx, sy] = 0.7   # Start cell in light gray
    display[gx, gy] = 0.9   # Goal cell in lighter gray

    plt.imshow(display, cmap="gray")
    plt.title("PathMind - Learned Path")
    plt.xticks([])
    plt.yticks([])
    plt.show()

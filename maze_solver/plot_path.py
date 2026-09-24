# plot_path.py

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def draw_maze(ax, maze, start, goal):
    # Same colours as the real maze: white = open floor, black = wall
    maze = np.array(maze)
    ax.imshow(maze, cmap=ListedColormap(["white", "black"]), vmin=0, vmax=1)
    ax.plot(start[1], start[0], "s", color="tab:green", markersize=14, label="Start")
    ax.plot(goal[1], goal[0], "*", color="tab:red", markersize=18, label="Goal")

    # Grid lines between cells
    ax.set_xticks(np.arange(-0.5, maze.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, maze.shape[0], 1), minor=True)
    ax.grid(which="minor", color="gray", linewidth=0.5)
    ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))


def plot_maze_with_path(maze, path, start, goal, save_to=None, show=True):
    fig, ax = plt.subplots()
    draw_maze(ax, maze, start, goal)

    rows = [x for x, _ in path]
    cols = [y for _, y in path]
    ax.plot(cols, rows, color="tab:blue", linewidth=3, marker="o", markersize=5)

    ax.set_title(f"PathMind - Learned Path ({len(path) - 1} moves)")
    fig.tight_layout()

    if save_to:
        fig.savefig(save_to, dpi=120)
        print(f"Saved plot to {save_to}")
    if show:
        plt.show()
    plt.close(fig)

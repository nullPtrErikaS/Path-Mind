# main.py

import argparse
import os
import sys

from maze_env import MazeEnv, load_maze, path_to_directions
from q_learning import train, greedy_path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    parser = argparse.ArgumentParser(description="Train a Q-learning agent to solve a maze.")
    parser.add_argument("--maze", default=os.path.join(ROOT, "maze.txt"), help="maze file to solve")
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--alpha", type=float, default=0.1, help="learning rate")
    parser.add_argument("--gamma", type=float, default=0.9, help="discount factor")
    parser.add_argument("--seed", type=int, default=None, help="random seed for repeatable runs")
    parser.add_argument("--out", default=os.path.join(ROOT, "learned_path.txt"),
                        help="where to save the learned path (one 'row,col' per line)")
    parser.add_argument("--save-plot", metavar="PNG", help="save the plot to an image file")
    parser.add_argument("--no-plot", action="store_true", help="don't open the plot window")
    args = parser.parse_args()

    maze, start, goal = load_maze(args.maze)
    print(f"Loaded {len(maze)}x{len(maze[0])} maze, start {start}, goal {goal}")

    env = MazeEnv(maze, start, goal)
    q_table = train(env, episodes=args.episodes, alpha=args.alpha, gamma=args.gamma, seed=args.seed)

    path = greedy_path(env, q_table)
    if path is None:
        sys.exit("Training finished but the agent can't reach the goal yet. "
                 "Try more --episodes, or check that the maze is solvable.")

    directions = path_to_directions(path)
    print(f"\nTraining complete. Learned path ({len(directions)} moves):")
    print(" -> ".join(f"({x},{y})" for x, y in path))
    print("Directions:", ", ".join(directions))

    # Save path to file for send_to_arduino.py
    with open(args.out, "w") as f:
        for x, y in path:
            f.write(f"{x},{y}\n")
    print(f"Saved path to {args.out}")

    if args.save_plot or not args.no_plot:
        from plot_path import plot_maze_with_path
        plot_maze_with_path(maze, path, start, goal, save_to=args.save_plot, show=not args.no_plot)


if __name__ == "__main__":
    main()

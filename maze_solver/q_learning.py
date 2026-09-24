# q_learning.py

import random

import numpy as np

from maze_env import ACTIONS


def train(env, episodes=1000, alpha=0.1, gamma=0.9,
          epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.995,
          max_steps=None, seed=None, verbose=True):
    """Train a tabular Q-learning agent on env. Returns the Q-table dict."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    if max_steps is None:
        max_steps = env.n_states * 4

    rows, cols = env.maze.shape
    q_table = {(x, y): [0.0] * len(ACTIONS) for x in range(rows) for y in range(cols)}

    for episode in range(episodes):
        state = env.reset()
        done = False
        steps = 0

        while not done and steps < max_steps:
            if random.uniform(0, 1) < epsilon:
                action = random.choice(ACTIONS)
            else:
                action = best_action(q_table[state])

            next_state, reward, done = env.step(action)

            old_value = q_table[state][action]
            next_max = 0.0 if done else max(q_table[next_state])
            q_table[state][action] = old_value + alpha * (reward + gamma * next_max - old_value)

            state = next_state
            steps += 1

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        if verbose and episode % 100 == 0:
            print(f"Episode {episode:4d}  steps {steps:4d}  epsilon {epsilon:.2f}")

    return q_table


def best_action(q_values):
    """argmax that breaks ties randomly, so untrained states don't always pick UP."""
    q_values = np.asarray(q_values)
    return int(random.choice(np.flatnonzero(q_values == q_values.max())))


def greedy_path(env, q_table):
    """Follow the learned policy from the start. Returns the list of cells
    visited (start and goal included), or None if the policy never reaches
    the goal (it walks into a wall or loops)."""
    env.reset()
    path = [env.agent_pos]
    visited = {env.agent_pos}

    for _ in range(env.n_states):
        action = int(np.argmax(q_table[env.agent_pos]))
        state, _, done = env.step(action)
        if state in visited:
            return None
        path.append(state)
        visited.add(state)
        if done:
            return path
    return None

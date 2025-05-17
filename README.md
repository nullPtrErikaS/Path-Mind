## PathMind: A Q-Learning Maze-Solving Robot

PathMind is a hybrid AI + robotics project that trains a virtual agent to solve mazes and then deploys that learned path to a real robot using an Arduino microcontroller.

### Features:
- Python-based Q-learning maze solver
- Visualization with matplotlib
- Serial communication to Arduino
- Arduino robot moves in white space, treats black as walls

### Setup Instructions
1. Run `main.py` to train a path
2. Send to robot using `send_to_arduino.py`
3. Upload `pathmind_robot.ino` to Arduino

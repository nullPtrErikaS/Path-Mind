## PathMind: A Q-Learning Maze-Solving Robot

PathMind is a hybrid AI + robotics project that trains a virtual agent to solve mazes and then deploys that learned path to a real robot using an Arduino microcontroller.

### Features:
- Python-based Q-learning maze solver
- Mazes loaded from a simple text file
- Visualization with matplotlib
- Serial communication to Arduino, with the robot confirming each move
- Arduino robot moves in white space, treats black as walls

### Project Layout
```
maze.txt                          the maze to solve
maze_solver/main.py               train the agent and save the learned path
maze_solver/maze_env.py           maze environment + maze file loader
maze_solver/q_learning.py         Q-learning training and path extraction
maze_solver/plot_path.py          draws the maze and learned path
maze_solver/send_to_arduino.py    sends the learned path to the robot
maze_solver/simulate.py           animated robot simulation, no hardware needed
maze_solver/robot_sim.py          simulated robot + fake serial port
arduino/pathmind_robot/           Arduino sketch for the robot
tests/                            unit tests
```

### Setup Instructions
1. Install the Python packages:
   ```
   pip install -r requirements.txt
   ```
2. Upload `arduino/pathmind_robot/pathmind_robot.ino` to the Arduino.
3. Train a path (this saves `learned_path.txt` and shows a plot):
   ```
   cd maze_solver
   python main.py
   ```
4. Place the robot on the start cell, facing `START_HEADING` (set in the sketch; default is facing DOWN, toward the bottom row), then send the path:
   ```
   python send_to_arduino.py --port COM4
   ```
   Use `--dry-run` to just print the directions.

### Simulation (no robot needed)
```
cd maze_solver
python simulate.py
```
This sends the learned path through `send_to_arduino.py` to a simulated robot (`robot_sim.py`) that follows the same serial protocol and turning logic as the Arduino sketch, then animates it driving the maze. The simulated centre sensor stops the robot with `BLOCKED` if it drives over black. It uses `learned_path.txt` if it matches the maze, and otherwise trains a new path.

Useful options:
- `--turn-error 20` / `--drive-error -15`: make turns or forward moves that many percent off, to see what poor calibration of `turnTimeMs` / `cellTimeMs` does
- `--start-heading LEFT`: start the robot facing another way (default is `START_HEADING` from the sketch)
- `--save-gif sim.gif`: save the animation; `--no-show` to skip the window; `--speed 2` to play faster

### Making Your Own Maze
Edit `maze.txt`. Each line is one row of the maze, top row first:

| Character | Meaning |
|-----------|---------|
| `S` | start |
| `G` | goal |
| `#` or `1` | wall (black) |
| `.` or `0` | open floor (white) |

Lines starting with `# ` (hash followed by a space) are comments. Train on another file with `python main.py --maze path/to/maze.txt`. For bigger mazes, add `--episodes 3000`.

### How It Works
The agent starts knowing nothing. For each episode it walks the maze, mostly picking the move its Q-table currently rates best but sometimes a random one (epsilon-greedy, with randomness decreasing over time). Every step costs -1, bumping a wall costs -5, and reaching the goal gives +100, so the Q-values end up favouring the shortest route. After training, following the best-rated move from each cell gives the path.

The Python side sends absolute directions (UP / DOWN / LEFT / RIGHT on the maze drawing). The robot remembers which way it is facing, turns to face the needed direction, then drives forward one cell. After each move it replies `OK`, or `BLOCKED` if its center sensor sees black (a wall), in which case the sender stops.

### Calibrating the Robot
The robot moves by timing, so tune these constants at the top of the sketch for your motors and maze size:
- `cellTimeMs`: how long to drive to move exactly one cell
- `turnTimeMs`: how long to spin to turn exactly 90 degrees
- `wallThreshold`: open the Serial Monitor (9600 baud), send `SENSE` with the sensor over white and then over black, and pick a value in between. If your sensor reads *higher* on black, flip the `<` in `isWallAhead()`.

### Running Without a Computer
Run `python send_to_arduino.py --print-array`, paste the printed line over `path[]` in the sketch, set `runStoredPath = true`, and upload. The robot will drive the path on power-up.

### Tests
```
python -m unittest discover -s tests
```

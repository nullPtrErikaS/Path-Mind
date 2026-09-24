// === PathMind robot ===
// Receives maze directions (UP / DOWN / LEFT / RIGHT) over serial, one per line,
// and drives one cell per direction. The directions are absolute (UP = toward the
// top row of the maze), so the robot keeps track of which way it is facing and
// turns before driving forward.
//
// Serial commands (9600 baud, newline-terminated):
//   UP, DOWN, LEFT, RIGHT  move one cell  -> replies "OK", or "BLOCKED" if a wall is seen
//   RESET                  robot is back on the start cell facing START_HEADING -> "OK"
//   SENSE                  print raw sensor readings (for calibration) -> "OK"

// === Motor Pins ===
// Note: on an Uno, pin 4 is not PWM, so analogWrite() on it is just on/off
// (on when motorSpeed >= 128). Move it to 9, 10 or 11 if you want speed control.
const int leftMotorFwd = 3;
const int leftMotorBack = 4;
const int rightMotorFwd = 5;
const int rightMotorBack = 6;

// === Sensor Pins ===
const int leftSensor = A0;
const int centerSensor = A1;
const int rightSensor = A2;

// === Movement Settings (calibrate these on your maze) ===
const int motorSpeed = 180;        // 0–255 PWM
const int wallThreshold = 500;     // use SENSE on white and black to pick a value in between
const unsigned long cellTimeMs = 800;  // time to drive forward exactly one cell
const unsigned long turnTimeMs = 450;  // time to spin exactly 90 degrees
const bool checkForWalls = true;   // stop if the center sensor sees black while driving

// === Headings (clockwise order, so turning right = +1) ===
const int HEADING_UP = 0;
const int HEADING_RIGHT = 1;
const int HEADING_DOWN = 2;
const int HEADING_LEFT = 3;

// Which way the robot faces when you place it on the start cell
const int START_HEADING = HEADING_DOWN;
int heading = START_HEADING;

// === Stored Path (optional) ===
// To run without a computer attached: run
//   python send_to_arduino.py --print-array
// paste the result here, and set runStoredPath to true.
const bool runStoredPath = false;
const char* path[] = {"DOWN", "DOWN", "RIGHT", "RIGHT", "DOWN", "DOWN", "RIGHT", "RIGHT"};
const int pathLength = sizeof(path) / sizeof(path[0]);

// === Setup ===
void setup() {
  Serial.begin(9600);
  pinMode(leftMotorFwd, OUTPUT);
  pinMode(leftMotorBack, OUTPUT);
  pinMode(rightMotorFwd, OUTPUT);
  pinMode(rightMotorBack, OUTPUT);
  stopMotors();
  Serial.println("PathMind starting...");
  delay(1000);

  if (runStoredPath) {
    for (int i = 0; i < pathLength; i++) {
      Serial.print("Stored path: ");
      Serial.println(path[i]);
      if (!followDirection(String(path[i]))) {
        Serial.println("BLOCKED");
        break;
      }
    }
    Serial.println("Stored path done");
  }

  Serial.println("READY");
}

// === Wait for commands from send_to_arduino.py ===
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // clean newline
    cmd.toUpperCase();
    if (cmd.length() == 0) return;

    Serial.print("Received: ");
    Serial.println(cmd);

    if (cmd == "RESET") {
      heading = START_HEADING;
      Serial.println("OK");
    } else if (cmd == "SENSE") {
      printSensors();
      Serial.println("OK");
    } else if (directionToHeading(cmd) < 0) {
      Serial.println("ERR unknown command");
    } else if (followDirection(cmd)) {
      Serial.println("OK");
    } else {
      Serial.println("BLOCKED");
    }
  }
}

// === Direction Logic ===
int directionToHeading(String dir) {
  if (dir == "UP") return HEADING_UP;
  if (dir == "RIGHT") return HEADING_RIGHT;
  if (dir == "DOWN") return HEADING_DOWN;
  if (dir == "LEFT") return HEADING_LEFT;
  return -1;
}

// Turn to face dir, then drive one cell. Returns false if a wall stopped us.
bool followDirection(String dir) {
  int target = directionToHeading(dir);
  if (target < 0) return false;

  int turns = (target - heading + 4) % 4;  // 0 = straight, 1 = right, 2 = around, 3 = left
  if (turns == 1) {
    turn90(true);
  } else if (turns == 2) {
    turn90(true);
    turn90(true);
  } else if (turns == 3) {
    turn90(false);
  }
  heading = target;

  return driveOneCell();
}

void turn90(bool right) {
  if (right) turnRight();
  else turnLeft();
  delay(turnTimeMs);
  stopMotors();
  delay(150);  // let the robot settle
}

bool driveOneCell() {
  moveForward();
  unsigned long startTime = millis();
  while (millis() - startTime < cellTimeMs) {
    if (checkForWalls && isWallAhead()) {
      stopMotors();
      return false;
    }
    delay(5);
  }
  stopMotors();
  delay(150);
  return true;
}

// === Motor Control ===
void moveForward() {
  stopMotors();
  analogWrite(leftMotorFwd, motorSpeed);
  analogWrite(rightMotorFwd, motorSpeed);
}

void moveBackward() {
  stopMotors();
  analogWrite(leftMotorBack, motorSpeed);
  analogWrite(rightMotorBack, motorSpeed);
}

void turnLeft() {
  stopMotors();
  analogWrite(leftMotorBack, motorSpeed);
  analogWrite(rightMotorFwd, motorSpeed);
}

void turnRight() {
  stopMotors();
  analogWrite(leftMotorFwd, motorSpeed);
  analogWrite(rightMotorBack, motorSpeed);
}

void stopMotors() {
  analogWrite(leftMotorFwd, 0);
  analogWrite(leftMotorBack, 0);
  analogWrite(rightMotorFwd, 0);
  analogWrite(rightMotorBack, 0);
}

// === Sensors ===
// Black tape = wall. With most IR reflectance sensors, black reflects less light.
// If your sensor reads HIGHER on black, flip the < to >.
bool isWallAhead() {
  int centerVal = analogRead(centerSensor);
  return centerVal < wallThreshold;
}

void printSensors() {
  Serial.print("Sensors L/C/R: ");
  Serial.print(analogRead(leftSensor));
  Serial.print(" / ");
  Serial.print(analogRead(centerSensor));
  Serial.print(" / ");
  Serial.println(analogRead(rightSensor));
}

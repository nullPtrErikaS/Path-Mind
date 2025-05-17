// === Motor Pins ===
const int leftMotorFwd = 3;
const int leftMotorBack = 4;
const int rightMotorFwd = 5;
const int rightMotorBack = 6;

// === Sensor Pins ===
const int leftSensor = A0;
const int centerSensor = A1;
const int rightSensor = A2;

// === Movement Settings ===
const int motorSpeed = 180;  // 0–255 PWM
const int wallThreshold = 500;  // adjust based on testing

// === Learned Path ===
String path[] = {"RIGHT", "RIGHT", "DOWN", "DOWN"};
const int pathLength = sizeof(path) / sizeof(path[0]);

// === Setup ===
void setup() {
  Serial.begin(9600);
  pinMode(leftMotorFwd, OUTPUT);
  pinMode(leftMotorBack, OUTPUT);
  pinMode(rightMotorFwd, OUTPUT);
  pinMode(rightMotorBack, OUTPUT);
  Serial.println("PathMind starting...");
  delay(1000);
}

// === Loop through path directions ===
void loop() {
  if (Serial.available()) {
    String dir = Serial.readStringUntil('\n');
    dir.trim(); // clean newline
    Serial.print("Received: ");
    Serial.println(dir);
    followDirection(dir);
    delay(1000);
  }
}

// === Direction Logic ===
void followDirection(String dir) {
  if (dir == "UP") moveForward();
  else if (dir == "DOWN") moveBackward();
  else if (dir == "LEFT") turnLeft();
  else if (dir == "RIGHT") turnRight();

  delay(500);  // move duration
  stopMotors();
}

// === Motor Control ===
void moveForward() {
  analogWrite(leftMotorFwd, motorSpeed);
  analogWrite(rightMotorFwd, motorSpeed);
}

void moveBackward() {
  analogWrite(leftMotorBack, motorSpeed);
  analogWrite(rightMotorBack, motorSpeed);
}

void turnLeft() {
  analogWrite(leftMotorBack, motorSpeed);
  analogWrite(rightMotorFwd, motorSpeed);
}

void turnRight() {
  analogWrite(leftMotorFwd, motorSpeed);
  analogWrite(rightMotorBack, motorSpeed);
}

void stopMotors() {
  analogWrite(leftMotorFwd, 0);
  analogWrite(leftMotorBack, 0);
  analogWrite(rightMotorFwd, 0);
  analogWrite(rightMotorBack, 0);
}

// === Obstacle Avoidance (optional) ===
bool isWallAhead() {
  int centerVal = analogRead(centerSensor);
  return centerVal < wallThreshold;
}

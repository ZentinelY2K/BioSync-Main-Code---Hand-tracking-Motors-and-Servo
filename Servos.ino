#include <Servo.h>

Servo thumbServo;

const int servoPin = 3;

// Motor 1 (Index)
const int ENA = 11;
const int IN1 = 7;
const int IN2 = 8;

// Motor 2 (Middle)
const int ENB = 5;
const int IN3 = 9;
const int IN4 = 10;

void setup() {
  Serial.begin(9600);
  thumbServo.attach(servoPin);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    int indexPWM, middlePWM, thumbAngle;
    int firstComma = input.indexOf(',');
    int secondComma = input.indexOf(',', firstComma + 1);

    if (firstComma > 0 && secondComma > firstComma) {
      indexPWM = input.substring(0, firstComma).toInt();
      middlePWM = input.substring(firstComma + 1, secondComma).toInt();
      thumbAngle = input.substring(secondComma + 1).toInt();

      analogWrite(ENA, indexPWM);
      analogWrite(ENB, middlePWM);
      thumbServo.write(thumbAngle);
    }
  }
}


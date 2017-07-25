#define lickSerial Serial1

char ri;
char cBuf[1];
int lickSensorA = 0;
int lickSensorB = 0;
int lastA = 0;
int lastB = 0;
bool startA = 0;
String tStr = "";
bool inA = 0;
bool inB = 0;
bool strAvail = 0;
bool rNewLine = 0;
int charCount = 0;
char lastSerState;




unsigned long lastTime = micros();



void setup() {
  Serial.begin(115200);
  lickSerial.begin(115200);
}

void loop() {
  pollLickSensors();
  lastA = lickSensorA;
  lastB = lickSensorB;
  delayMicroseconds(1000);
}



void pollLickSensors() {
  if (lickSerial.available() > 0) {
    ri = lickSerial.read();
  }
  // new line case
  if (ri == '\n') {
    rNewLine = 1;
    charCount = 0;
    tStr = "";
  }
  else if (ri == 'a') {
    lastSerState = 'a';
    charCount = 0;
    tStr = "";
  }
  else if (ri == 'b') {
    lastSerState = 'b';
    charCount = 0;
    tStr = "";
  }
  else if (isDigit(ri)) {
    tStr = String(tStr + ri);
    charCount++;
    if (charCount == 5) {
      if (lastSerState == 'a') {
        lickSensorA = int(tStr.toInt());
      }
      else if (lastSerState == 'b') {
        lickSensorB = int(tStr.toInt());
      }
      tStr = "";
    }
  }
}


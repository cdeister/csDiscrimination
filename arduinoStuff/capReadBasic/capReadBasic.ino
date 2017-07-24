#define capSer Serial1

char ri;
char cBuf[1];
int lastA = 0;
int lastB = 0;
bool startA = 0;
String tStr = "";
bool inA = 0;
bool inB = 0;
int delayTime = 1000;
bool strAvail = 0;
bool lastState = 0;
int stateCount = 0;


unsigned long lastTime = micros();



void setup() {
  Serial.begin(115200);
  capSer.begin(115200);
}

void loop() {
  if (capSer.available() > 0) {
    delayTime = 1000;
    ri = capSer.read();

    if (ri == 'a') {
      inA = 1; inB = 0;
      stateCount = 0;
      if (strAvail == 1 && lastState == 0) {
        lastA = tStr.toInt();
        tStr = "";
        strAvail = 0;
      }
      else if (strAvail == 1 && lastState == 1) {
        lastB = tStr.toInt();
        tStr = "";
        strAvail = 0;
      }
    }

    else if (ri == 'b') {
      inA = 0; inB = 1;
      stateCount = 0;
      if (strAvail == 1 && lastState == 0) {
        lastA = tStr.toInt();
        tStr = "";
        strAvail = 0;
      }
      else if (strAvail == 1 && lastState == 1) {
        lastB = tStr.toInt();
        tStr = "";
        strAvail = 0;
      }
    }

    if (inA == 1 && stateCount > 0) {
      tStr = (tStr + ri);
      strAvail = 1;
      lastState = 0;
    }

    else if (inB == 1 && stateCount > 0) {
      tStr = (tStr + ri);
      strAvail = 1;
      lastState = 1;
    }
    stateCount++;
  }
    Serial.print(lastA);
    Serial.print(',');
    Serial.println(lastB);
  Serial.println(micros() - lastTime);
  lastTime = micros();
  delayMicroseconds(delayTime);
}


void parseRemoteSensors(){
  
}








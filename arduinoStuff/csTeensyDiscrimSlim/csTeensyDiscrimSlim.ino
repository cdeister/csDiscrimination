/*
  csTeensyDiscrim
  Main Teensy Script For Discrim Task. Assumes a 3.5/6 teensy for speed sake.
  Will work with any MC swith a hardware serial port.
  v1.0 -- cdeister@brown.edu

*/

// motion vars
#define motionSerial Serial1
int motionBaud = 9600;

// lick vars
int lickSensorL = 0;
int lickSensorR = 0;

bool useThermal = 0;


int loopDelta = 1000; //in microseconds

int toneLow = 100;
int toneHigh = 1000;
int rewardTime = 60000;  // micros
int rewardBlockTime = 2000000;


unsigned long msOffset;
unsigned long s1Offset;
unsigned long trialTimeMicro;
unsigned long stateTimeMicro;
unsigned long pulseTime;
unsigned long delayTime;
unsigned long pulseOffset;
unsigned long delayOffset;

int lastState;
int curState;
int headerState;

bool stateChange = 0;
bool inPulse = 0;
bool cueInit = 0;
bool headerFired = 0;

const int waterLPin = 15;   // Engage Water
const int waterRPin = 16;   // Engage Water
const int cue1LED = 13;
const int cue2LED = 13;
const int initLED = 13;
const int toLED = 9;

const int tonePin = 6;

const int lickPinL = 23;
const int lickPinR = 19;

/* vars for split read */

const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
int lastOrient = 0;
int readOrient = 0;;
int orientDelta = 0;
char ff;

/* ~~~~~~~~~~~~~~~~~~~~~~~~ */


void setup() {
  pinMode(initLED, OUTPUT);
  pinMode(toLED, OUTPUT);
  pinMode(waterLPin, OUTPUT);
  pinMode(waterRPin, OUTPUT);
  pinMode(tonePin, OUTPUT);
  pinMode(cue1LED, OUTPUT);
  pinMode(cue2LED, OUTPUT);
  pinMode(lickPinL, INPUT);
  pinMode(lickPinR, INPUT);


  Serial.begin(115200); // initialize Serial communication
  motionSerial.begin(motionBaud);
  while (!Serial);    // wait for the serial port to open
  Serial.println("Start");
  delay(500);
  msOffset = micros();
  s1Offset = micros();
  pulseOffset = micros();
  delayOffset = micros();
  headerFired = 0;
  establishOrder();
}

void loop() {

  if (curState == 2) {
    s1Offset = micros();
    establishOrder();
    digitalWrite(initLED, HIGH);
    headerFired = 0;
    pulseOffset = micros();
    delayOffset = micros();
    headerState = curState;

    headerFired = 1;

    while (headerFired == 1 and headerState == curState) {
      headerFired = 1;
      genericReport();
    }
  }

  else if (curState == 3) {
    s1Offset = micros();
    nonBlockBlink(20000, 50000, 1, cue1LED);
  }
  else if (curState == 4) {
    s1Offset = micros();
    nonBlockBlink(20000, 200000, 1, cue2LED);
  }
  else if (curState == 5) {
    s1Offset = micros();
    toneState(tonePin, toneLow);
  }
  else if (curState == 6) {
    s1Offset = micros();
    toneState(tonePin, toneHigh);
  }

  else if (curState == 21) {
    s1Offset = micros();
    nonBlockBlink(rewardTime, rewardBlockTime, 1, waterLPin);
  }

  else if (curState == 22) {
    s1Offset = micros();
    nonBlockBlink(rewardTime, rewardBlockTime, 1, waterRPin);
  }

  else if (curState == 24) {
    s1Offset = micros();
    nonBlockBlink(20000, 100000, 1, toLED);
  }


  else {
    s1Offset = micros();
    genericState();
  }
}




// ---------- Helper Functions


int lookForSerialState() {
  int pyState;
  if (Serial.available() > 0) {
    pyState = Serial.read();
    lastState = pyState;
    stateChange = 1;
  }
  else if (Serial.available() <= 0) {
    pyState = lastState;
    stateChange = 0;
  }
  return pyState;
}


void establishOrder() {
  noTone(tonePin);
  digitalWrite(waterLPin, LOW);
  digitalWrite(waterRPin, LOW);
  digitalWrite(initLED, LOW);
}


int spitData(unsigned long d1, unsigned long d2, int d3, int d4, int d5, int d6) {
  Serial.print("data,"); Serial.print(d1); Serial.print(','); Serial.print(d2);
  Serial.print(','); Serial.print(d3); Serial.print(','); Serial.print(d4);
  Serial.print(','); Serial.print(d5); Serial.print(','); Serial.print(d6);
  Serial.println();
}

void toneState(int tPin, int tFreq) {
  establishOrder();
  tone(tPin, tFreq);
  headerFired = 0;
  pulseOffset = micros();
  delayOffset = micros();
  headerState = curState;
  headerFired = 1;

  while (headerFired == 1 and headerState == curState) {
    headerFired = 1;
    genericReport();
  }
}

void genericState() {
  // header component
  establishOrder();
  headerFired = 0;
  pulseOffset = micros();
  delayOffset = micros();
  headerState = curState;
  headerFired = 1;
  while (headerFired == 1 and headerState == curState) {
    headerFired = 1;
    genericReport();
  }

}

void nonBlockBlink(int pT, int dT, int startOnOrOff, int pinNum) {
  // header component
  establishOrder();
  headerFired = 0;
  pulseOffset = micros();
  delayOffset = micros();
  headerState = curState;
  headerFired = 1;

  // header component
  while (headerFired == 1 and headerState == curState) {
    pulseTime = micros() - pulseOffset;
    delayTime = micros() - delayOffset;

    if (startOnOrOff == 0) {
      if (delayTime > dT) {
        digitalWrite(pinNum, HIGH);
        pulseOffset = micros();
        startOnOrOff = 1;
      }
      else if (delayTime <= dT) {
        digitalWrite(pinNum, LOW);
        pulseOffset = micros();
        startOnOrOff = 0;
      }
    }
    if (startOnOrOff == 1) {
      if (pulseTime > pT) {
        digitalWrite(pinNum, LOW);
        delayOffset = micros();
        startOnOrOff = 0;
      }
      else if (delayTime <= pT) {
        digitalWrite(pinNum, HIGH);
        delayOffset = micros();
        startOnOrOff = 1;
      }
    }
    headerFired = 1;
    genericReport();
  }
}

void genericReport() {
  trialTimeMicro = micros() - msOffset;
  stateTimeMicro = micros() - s1Offset;
  pollLickSensors();
  flagReceive('o', '>');
  showNewData();
  spitData(trialTimeMicro, stateTimeMicro, readOrient, curState, lickSensorL, lickSensorR);
  delayMicroseconds(loopDelta);
  curState = lookForSerialState();
}

void pollLickSensors() {
  lickSensorR = analogRead(lickPinR);
  lickSensorL = analogRead(lickPinL);
  //  lickSensorR=map(analogRead(lickPinR),0,1024,1000,0); uncomment for a cap breakout
  //  lickSensorL=map(analogRead(lickPinL),0,1024,1000,0);
}

void flagReceive(char startChars, char endChars) {
  static boolean recvInProgress = false;
  static byte ndx = 0; char startMarker = startChars;
  char endMarker = endChars; char rc;

  while (motionSerial.available() > 0 && newData == false) {
    rc = motionSerial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else if (rc == endMarker ) {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }
    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void showNewData() {
  if (newData == true) {
    readOrient = int(String(receivedChars).toInt());
    lastOrient = readOrient;
    newData = false;
  }
}


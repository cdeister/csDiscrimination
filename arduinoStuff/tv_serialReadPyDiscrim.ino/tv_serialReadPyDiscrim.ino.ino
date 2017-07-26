/*
   See how they run
   Three blind mice
*/

// I could do states with switch, but seems unecessary.
// I assume switch is more efficient http://www.blackwasp.co.uk/SpeedTestIfElseSwitch.aspx
// However, seems like it is negligible

#define motionSerial Serial4

// lick vars
int lickSensorL = 0;
int lickSensorR = 0;

bool useThermal=0;


int loopDelta = 1000; //in microseconds

int toneLow = 100;
int toneHigh = 1000;
int rewardTime = 200;  // in millis!
int rewardBlockTime = 1000;

int last9dof = 0;
int cur9dof = 0;
int dif9dof = 0;

int toneTimer;
int toneOffset;

int rangeDelta = 0;
float ldLux = 0;

int rewardLatch = 0; // not bool so we can count if needed later

unsigned long msOffset;
unsigned long s1Offset;
unsigned long trialTimeMicro;
unsigned long stateTimeMicro;
unsigned long cueTime;
unsigned long pulseTime;
unsigned long delayTime;
unsigned long pulseOffset;
unsigned long delayOffset;
unsigned long rewardTimer;
unsigned long punishOffset;
unsigned long lastTime;

int currentPosDelta = 128;
int lastPosition = 0;
int absolutePosition;

int lastState;
int curState;
int headerState;

bool stateChange = 0;
bool cueFired = 0;
bool toneFired = 0;
bool inPulse = 1;
bool cueInit = 0;
bool headerFired = 0;

const int posPin = 3;     // Engage Postive Reinforcment
const int negPin = 4;     // Engage Aversive Reinforcment
const int waterLPin = 15;   // Engage Water
const int waterRPin = 16;   // Engage Water
const int cueLED = 13;
const int tonePin = 22;
const int lickPinL = A9;
const int lickPinR = A5;


void setup() {
  pinMode(posPin, OUTPUT);
  pinMode(negPin, OUTPUT);
  pinMode(waterLPin, OUTPUT);
  pinMode(waterRPin, OUTPUT);
  pinMode(tonePin, OUTPUT);
  pinMode(cueLED, OUTPUT);


  Serial.begin(9600); // initialize Serial communication
  motionSerial.begin(19200);
  while (!Serial);    // wait for the serial port to open
  Serial.println("Start");
  delay(500);
  msOffset = micros();
  s1Offset = micros();
  pulseOffset = millis();
  delayOffset = millis();
  inPulse = 0;
  headerFired = 0;
  establishOrder();
  lastTime = 0;
}

void loop() {
  if (curState == 0) {
    msOffset = micros();
    genericState();
  }
  if (curState == 3) {
    s1Offset = micros();
    nonBlockBlink(10, 40, 0, cueLED);
  }

  if (curState == 4) {
    s1Offset = micros();
    nonBlockBlink(10, 200, 0, cueLED);
  }

  if (curState == 5) {
    s1Offset = micros();
    toneState(tonePin, toneLow);
  }

  if (curState == 6) {
    s1Offset = micros();
    toneState(tonePin, toneHigh);
  }

  else if (curState == 21 || curState == 22) {
    s1Offset = micros();
    nonBlockBlink(rewardTime, rewardBlockTime, 1, waterLPin);
  }

  else if (curState != 21 || curState != 22 || curState != 3 || curState != 4 || curState != 5 || curState != 6 || curState != 0) {
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


//int poll9dof() {
//  if (motionSerial.available() > 0) {
//    cur9dof = motionSerial.parseInt() + 180;
//  }
//  //  dif9dof = (cur9dof - last9dof)/(millis()-lastTime);
//  //  last9dof=cur9dof;
//  //  lastTime=millis();
//}

int pollOpticalMouse() {
  currentPosDelta = 128;
  if (motionSerial.available() > 0) {
    currentPosDelta = motionSerial.parseInt();
  }
  else if (motionSerial.available() <= 0) {
    currentPosDelta = 128;
  }
}

void establishOrder() {
  noTone(tonePin);
  digitalWrite(waterLPin, LOW);
  digitalWrite(cueLED, LOW);
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
  pulseOffset = millis();
  delayOffset = millis();
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
  pulseOffset = millis();
  delayOffset = millis();
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
  pulseOffset = millis();
  delayOffset = millis();
  headerState = curState;
  headerFired = 1;

  // header component
  while (headerFired == 1 and headerState == curState) {
    pulseTime = millis() - pulseOffset;
    delayTime = millis() - delayOffset;

    if (startOnOrOff == 0) {
      if (delayTime > dT) {
        digitalWrite(pinNum, HIGH);
        pulseOffset = millis();
        startOnOrOff = 1;
      }
      else if (delayTime <= dT) {
        digitalWrite(pinNum, LOW);
        pulseOffset = millis();
        startOnOrOff = 0;
      }
    }
    // deal with pulse
    if (startOnOrOff == 1) {
      if (pulseTime > pT) {
        digitalWrite(pinNum, LOW);
        delayOffset = millis();
        startOnOrOff = 0;
      }
      else if (delayTime <= pT) {
        digitalWrite(pinNum, HIGH);
        delayOffset = millis();
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
  //  pollOpticalMouse();
  pollLickSensors();
  spitData(trialTimeMicro, stateTimeMicro, cur9dof, curState, lickSensorL, lickSensorR);

  delayMicroseconds(loopDelta);
  digitalWrite(cueLED, LOW);
  curState = lookForSerialState();
}

void pollLickSensors(){
  lickSensorR=analogRead(lickPinR);
  lickSensorL=analogRead(lickPinL);
}



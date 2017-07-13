/*
   See how they run
   Three blind mice
*/

// I could do states with switch, but seems unecessary.
// I assume switch is more efficient http://www.blackwasp.co.uk/SpeedTestIfElseSwitch.aspx
// However, seems like it is negligible

#define mpSerial Serial3


int loopDelta = 1000; //in microseconds
int pulseDur = 40;
int delayDur_1 = 200;
int delayDur_2 = 20;
int cueDelay=500;
int toneDelay=1000;
int toneTime=5000;
int toneLow=900;
int toneHigh=1400;
int toneTimer;
int toneOffset;
int lickValues_a = 0;
int lickValues_b = 0;
int rewardLatch = 0; // not bool so we can count if needed later
int rewardTime = 100; //in ms
//int punishTime=5000;

unsigned long msOffset;
unsigned long s1Offset;
unsigned long msCorrected;
unsigned long msInTrial;
unsigned long cueTime;
unsigned long pulseTime;
unsigned long delayTime;
unsigned long pulseOffset;
unsigned long delayOffset;
unsigned long rewardTimer;
unsigned long punishTimer;
unsigned long rewardOffset;
unsigned long punishOffset;

int currentPosDelta = 128;
long lastPosition = 0;
long absolutePosition;

int lastState;
int curState;

bool stateChange = 0;
bool cueFired = 0;
bool toneFired = 0;
bool inPulse = 1;
bool cueInit = 0;
bool bef = 0;

const int posPin = 3;     // Engage Postive Reinforcment
const int negPin = 4;     // Engage Aversive Reinforcment
const int waterPin = 13;   // Engage Water
const int cueLED = 13;
const int tonePin = 22;
const int posSensPin_a = 0;
const int posSensPin_b = 2;
const int capSensPin_a=15;
const int capSensPin_b=16;


void setup() {
  pinMode(posPin, OUTPUT);
  pinMode(negPin, OUTPUT);
  pinMode(waterPin, OUTPUT);
  pinMode(tonePin, OUTPUT);
  pinMode(cueLED, OUTPUT);


  Serial.begin(9600); // initialize Serial communication
  mpSerial.begin(19200);
  while (!Serial);    // wait for the serial port to open
  Serial.println("Start");
  delay(500);
  digitalWrite(cueLED, LOW);
  msOffset = micros();
  s1Offset = micros();
  establishOrder();
}

void loop() {
//////////
  //s3
  if (curState == 3) {
    establishOrder();
    bef = 0;
    while (bef == 0) {
      msOffset = micros();
      s1Offset = micros();
      pulseOffset = millis();
      delayOffset = millis();
      inPulse = 0;
      bef = 1;

    }
    while (bef == 1) {
      msCorrected = micros() - msOffset;
      msInTrial = micros() - s1Offset;
      pulseTime = millis() - pulseOffset;
      delayTime = millis() - delayOffset;
      
      if (inPulse==0) {
        if (delayTime > delayDur_1) {
          inPulse = 1;
        }
        digitalWrite(cueLED, LOW);
        pulseOffset=millis();
      }

      else if (inPulse==1) {
        if (pulseTime > pulseDur) {
          inPulse = 0;
        }
        digitalWrite(cueLED, HIGH);
        delayOffset=millis();
      }
      pollOpticalMouse();
      checkLicks();
      spitData(msCorrected, msInTrial, currentPosDelta, curState, lickValues_a, lickValues_b);
      delayMicroseconds(loopDelta);
      curState = lookForSerialState();
    }
  }

//////////
  //s4
  if (curState == 4) {
    establishOrder();
    bef = 0;
    while (bef == 0) {
      msOffset = micros();
      s1Offset = micros();
      pulseOffset = millis();
      delayOffset = millis();
      inPulse = 0;
      bef = 1;

    }
    while (bef == 1) {
      msCorrected = micros() - msOffset;
      msInTrial = micros() - s1Offset;
      pulseTime = millis() - pulseOffset;
      delayTime = millis() - delayOffset;
      
      if (inPulse==0) {
        if (delayTime > delayDur_2) {
          inPulse = 1;
        }
        digitalWrite(cueLED, LOW);
        pulseOffset=millis();
      }

      else if (inPulse==1) {
        if (pulseTime > pulseDur) {
          inPulse = 0;
        }
        digitalWrite(cueLED, HIGH);
        delayOffset=millis();
      }
      pollOpticalMouse();
      checkLicks();
      spitData(msCorrected, msInTrial, currentPosDelta, curState, lickValues_a, lickValues_b);
      delayMicroseconds(loopDelta);
      curState = lookForSerialState();
    }
  }

// S5: Sensory Low
else if (curState == 5) {
  establishOrder();
    bef = 0;
    while (bef == 0) {
      msOffset = micros();
      s1Offset = micros();
      pulseOffset = millis();
      delayOffset = millis();
      inPulse = 0;
      bef = 1;
      
      tone(tonePin, toneLow);
      toneOffset = millis();
    }
    while(bef==1){
      toneTimer = millis() - toneOffset;
      if (toneTimer > toneTime) {
        noTone(tonePin);
      }
      msCorrected = micros() - msOffset;
      msInTrial = micros() - s1Offset;
      spitData(msCorrected, msInTrial, currentPosDelta, curState, lickValues_a, lickValues_b);
      pollOpticalMouse();
      checkLicks();
      delayMicroseconds(loopDelta);
      curState = lookForSerialState();
    }
}
///

// S6: Sensory High
else if (curState == 6) {
  establishOrder();
    bef = 0;
    while (bef == 0) {
      msOffset = micros();
      s1Offset = micros();
      pulseOffset = millis();
      delayOffset = millis();
      inPulse = 0;
      bef = 1;

      tone(tonePin, toneHigh);
      toneOffset = millis();
    }
    while(bef==1){
      toneTimer = millis() - toneOffset;
      if (toneTimer > toneTime) {
        noTone(tonePin);
      }
      msCorrected = micros() - msOffset;
      msInTrial = micros() - s1Offset;
      spitData(msCorrected, msInTrial, currentPosDelta, curState, lickValues_a, lickValues_b);
      pollOpticalMouse();
      checkLicks();
      delayMicroseconds(loopDelta);
      curState = lookForSerialState();
    }
}
///



// S21: Reward State
else if (curState == 21) {
  establishOrder();
    bef = 0;
    while (bef == 0) {
      msOffset = micros();
      s1Offset = micros();
      rewardOffset = millis();
      inPulse = 0;
      bef = 1;
    }
 
    rewardTimer = millis() - rewardOffset;
    msCorrected = micros() - msOffset;
    msInTrial = micros() - s1Offset;
    spitData(msCorrected, msInTrial, currentPosDelta, curState, lickValues_a, lickValues_b);
    pollOpticalMouse();
    checkLicks();
    delayMicroseconds(loopDelta);
    if (rewardLatch==0){
      curState = lookForSerialState();
    }
    
    if (rewardTimer < rewardTime) {
      digitalWrite(waterPin, HIGH);
      curState = lookForSerialState();
      rewardLatch = 1;
    }
    else {
      digitalWrite(waterPin, LOW);
    rewardLatch = 0;
  }
}

else {
  establishOrder();
  bef = 0;
  while (bef == 0) {
    msOffset = micros();
    s1Offset = micros();
    bef = 1;
  }
  while (bef == 1) {
    msCorrected = micros() - msOffset; // total time
    msInTrial = micros() - s1Offset; // trial time
    pollOpticalMouse();
    checkLicks();
    spitData(msCorrected, msInTrial, currentPosDelta, curState, lickValues_a, lickValues_b);
    delayMicroseconds(loopDelta);
    curState = lookForSerialState();
  }
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

int pollOpticalMouse() {
  //  currentPosDelta=128;
  if (mpSerial.available() > 0) {
    currentPosDelta = mpSerial.parseInt();
  }
  else if (mpSerial.available() <= 0) {
    currentPosDelta = 128;
  }
}

void checkLicks() {
  lickValues_a = touchRead(15);
  lickValues_b = touchRead(16);
}

void establishOrder() {
  noTone(tonePin);
  digitalWrite(waterPin, LOW);
  digitalWrite(cueLED, LOW);
}


int spitData(unsigned long d1, unsigned long d2, int d3, int d4, int d5, int d6) {
  Serial.print("data,");
  Serial.print(d1);
  Serial.print(',');
  Serial.print(d2);
  Serial.print(',');
  Serial.print(d3);
  Serial.print(',');
  Serial.print(d4);
  Serial.print(',');
  Serial.print(d5);
  Serial.print(',');
  Serial.print(d6);
  Serial.println();
}

//-----------------------




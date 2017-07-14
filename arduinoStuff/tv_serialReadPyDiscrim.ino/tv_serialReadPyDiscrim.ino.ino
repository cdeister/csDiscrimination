/*
   See how they run
   Three blind mice
*/

// I could do states with switch, but seems unecessary.
// I assume switch is more efficient http://www.blackwasp.co.uk/SpeedTestIfElseSwitch.aspx
// However, seems like it is negligible

#define mpSerial Serial3


int loopDelta = 1000; //in microseconds

int toneDelay=1000;
int toneTime=5000;
int toneLow=900;
int toneHigh=1400;
int rewardTime = 100;  // in millis!
int rewardBlockTime=1000;

int toneTimer;
int toneOffset;

int lickSensorA = 0;
int lickSensorB = 0;

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

int currentPosDelta = 128;
long lastPosition = 0;
long absolutePosition;

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
const int waterPin = 13;   // Engage Water
const int cueLED = 13;
const int tonePin = 22;
const int posSensPin_a = 0;
const int posSensPin_b = 2;


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
  msOffset = micros();
  s1Offset = micros();
  pulseOffset = millis();
  delayOffset = millis();
  inPulse = 0;
  headerFired=0;
  establishOrder();
}

void loop() {
  if (curState==0){
    msOffset=micros(); 
    // I will reset the trial with a call to 0, so this can reset the trial time.
    // just a convinence anyway, we just need time deltas and states, rest is convinence.
    genericState();
  }
  if (curState==3){
    s1Offset=micros();
    nonBlockBlink(10,100,1,cueLED);
  }

  if (curState==4){
    s1Offset=micros();
    nonBlockBlink(10,500,1,cueLED);
  }

  else if (curState==21){
    s1Offset=micros();
    nonBlockBlink(rewardTime,rewardBlockTime,1,waterPin);
  }

  else if (curState!=21 || curState!=3 || curState!=4 || curState!=0){
    s1Offset=micros();
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

int pollOpticalMouse() {
  //  currentPosDelta=128;
  if (mpSerial.available() > 0) {
    currentPosDelta = mpSerial.parseInt();
  }
  else if (mpSerial.available() <= 0) {
    currentPosDelta = 128;
  }
}

void establishOrder() {
  noTone(tonePin);
  digitalWrite(waterPin, LOW);
  digitalWrite(cueLED, LOW);
}


int spitData(unsigned long d1, unsigned long d2, int d3, int d4, int d5, int d6) {
  Serial.print("data,"); Serial.print(d1); Serial.print(','); Serial.print(d2);
  Serial.print(','); Serial.print(d3); Serial.print(','); Serial.print(d4);
  Serial.print(','); Serial.print(d5); Serial.print(','); Serial.print(d6); 
  Serial.println();
}

void genericState(){
  // header component
  establishOrder();
  headerFired=0;
  pulseOffset=millis();
  delayOffset=millis();
  headerState=curState;
  headerFired=1;

  while(headerFired==1 and headerState==curState){
    headerFired=1;
    genericReport();
  }
  
}

void nonBlockBlink(int pT, int dT, int startOnOrOff, int pinNum) {
  // header component
  establishOrder();
  headerFired=0;
  pulseOffset=millis();
  delayOffset=millis();
  headerState=curState;
  headerFired=1;
  
  // header component
  while(headerFired==1 and headerState==curState){
    pulseTime=millis()-pulseOffset;
    delayTime=millis()-delayOffset;

    if (startOnOrOff==0){
      if (delayTime>dT){
        digitalWrite(pinNum, HIGH);
        pulseOffset=millis();
        startOnOrOff=1;
      }
      else if(delayTime<=dT){
        digitalWrite(pinNum, LOW);
        pulseOffset=millis();
        startOnOrOff=0;
      }
    }
    // deal with pulse
    if (startOnOrOff==1){
      if (pulseTime>pT){
        digitalWrite(pinNum, LOW);
        delayOffset=millis();
        startOnOrOff=0;
      }
      else if(delayTime<=pT){
        digitalWrite(pinNum, HIGH);
        delayOffset=millis();
        startOnOrOff=1;
      }
    }
    headerFired=1;
    genericReport();
  }
}

void genericReport(){
    trialTimeMicro=micros()-msOffset;
    stateTimeMicro=micros()-s1Offset;
    pollOpticalMouse();
    spitData(trialTimeMicro,stateTimeMicro,currentPosDelta,curState,lickSensorA,lickSensorB);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
    Serial.print("meta,");
    Serial.println(curState);
}




//-----------------------

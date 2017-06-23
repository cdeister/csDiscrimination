/*
 * See how they run
 * Three blind mice
 */

// I could do states with switch, but seems unecessary.
// I assume switch is more efficient http://www.blackwasp.co.uk/SpeedTestIfElseSwitch.aspx
// However, seems like it is negligible

#define mpSerial Serial1


int loopDelta=1000;
int cueDuration=2000;
int pulseDur=40;
int delayDur_1=200;
int delayDur_2=20;
int cueDelay=500;
int toneDelay=1000;
int toneTime=2000;
int toneTimer;
int toneOffset;
int lickValues_a=0;
int lickValues_b=0;

unsigned long msOffset;
unsigned long s1Offset;
unsigned long msCorrected;
unsigned long msInTrial;

unsigned long cueTime;
unsigned long pulseTime;
unsigned long delayTime;
unsigned long ofs1;
unsigned long ofs2;
unsigned long ofs3;

int currentPosDelta=128;
long lastPosition=0;
long absolutePosition;

int lastState;
int curState;

bool stateChange=0;
bool cueFired=0;
bool toneFired=0;
bool inPulse=1;
bool cueInit=0;
bool bef=0;

const int posPin=3;       // Engage Postive Reinforcment
const int negPin=4;       // Engage Aversive Reinforcment
const int waterPin=6;     // Engage Water
const int cueLED=13;
const int tonePin=22;
const int posSensPin_a=0;
const int posSensPin_b=2;


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
  msOffset=micros();
  s1Offset=micros();
}

void loop() {
  // SO: Initialization State
  // This is just a state that ensures that the arduino lets python know 
  // it is ready to spit out real data and not garbage
  if(curState==0){
    // This toggles a bit to reset time at start.
    while(bef==0){
      msOffset=micros();
      s1Offset=micros();
      digitalWrite(cueLED,HIGH);
      bef=1;
    }
    msCorrected=micros()-msOffset;  // total time
    msInTrial=micros()-s1Offset;    // trial time
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }


  // S1: Trial wait state.
  else if(curState==1){
    curState=1;
    while(bef==1){
      s1Offset=micros();
      bef=0;
      digitalWrite(cueLED,LOW);
    }
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }

  // S2: Trial initiation state.
  else if(curState==2){
    cueFired=0;
    cueInit=0;
    bef=1;
    noTone(tonePin);
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }

  // S3: Sensory Task #1 Cue
  else if(curState==3){
    bef=1;
    // timestamp, dump data, check state
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    if(cueFired==0){
      if(cueInit==0){
        ofs1=millis();
        ofs2=millis();
        ofs3=millis();
        cueInit=1;
      }
      cueTime=millis()-ofs1;
      pulseTime=millis()-ofs2;
      delayTime=millis()-ofs3;
      if(cueTime<cueDuration){
        if(inPulse==1){
          pulseTime=millis()-ofs2;
          if(pulseTime<=pulseDur){
            inPulse=1;
            digitalWrite(cueLED,HIGH);
          }
          else if(pulseTime>pulseDur){
            inPulse=0;
            ofs3=millis();
          }
        }
        else if(inPulse==0){
          if(delayTime<=delayDur_1){
            inPulse=0;
            digitalWrite(cueLED,LOW);
          }
          else if(delayTime>delayDur_1){
            inPulse=1;
            ofs2=millis();
          }
        }
      }
      else if(cueTime>=cueDuration){
        digitalWrite(cueLED,LOW);
        cueFired=1;
        inPulse=1;
      }
    }
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }
  
  // S4: Sensory Task #2 Cue
  else if(curState==4){
    bef=1;
    // timestamp, dump data, check state
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    if(cueFired==0){
      if(cueInit==0){
        ofs1=millis();
        ofs2=millis();
        ofs3=millis();
        cueInit=1;
      }
      cueTime=millis()-ofs1;
      pulseTime=millis()-ofs2;
      delayTime=millis()-ofs3;
      if(cueTime<cueDuration){
        if(inPulse==1){
          pulseTime=millis()-ofs2;
          if(pulseTime<=pulseDur){
            inPulse=1;
            digitalWrite(cueLED,HIGH);
          }
          else if(pulseTime>pulseDur){
            inPulse=0;
            ofs3=millis();
          }
        }
        else if(inPulse==0){
          if(delayTime<=delayDur_2){
            inPulse=0;
            digitalWrite(cueLED,LOW);
          }
          else if(delayTime>delayDur_2){
            inPulse=1;
            ofs2=millis();
          }
        }
      }
      else if(cueTime>=cueDuration){
        digitalWrite(cueLED,LOW);
        cueFired=1;
        inPulse=1;
      }
    }
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    pollOpticalMouse();
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }
  
  // S5: Sensory High
  else if(curState==5){
    while(bef==1){
      tone(tonePin, 900);
      toneOffset=millis();
      bef=0;
    }
    toneTimer=millis()-toneOffset;
    if(toneTimer>toneTime){
      noTone(tonePin);
    }
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    pollOpticalMouse();
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }

  // S6: Sensory Low
  else if(curState==6){
    while(bef==1){
      tone(tonePin, 100);
      toneOffset=millis();
      bef=0;
    }
    toneTimer=millis()-toneOffset;
    if(toneTimer>toneTime){
      noTone(tonePin);
    }
    // timestamp, dump data, check state
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }

  // S7: Sensory High
  else if(curState==7){
    while(bef==1){
      tone(tonePin, 900);
      toneOffset=millis();
      bef=0;
    }
    toneTimer=millis()-toneOffset;
    if(toneTimer>toneTime){
      noTone(tonePin);
    }
    // timestamp, dump data, check state
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }

  // S8: Sensory Low
  else if(curState==8){
    while(bef==1){
      tone(tonePin, 100);
      toneOffset=millis();
      bef=0;
    };
    toneTimer=millis()-toneOffset;
    if(toneTimer>toneTime){
      noTone(tonePin);
    };
    // timestamp, dump data, check state
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }
  else {
    bef=0;
    noTone(tonePin);
    msCorrected=micros()-msOffset;
    msInTrial=micros()-s1Offset;
    pollOpticalMouse();
    spitData(msCorrected,msInTrial,currentPosDelta,curState,lickValues_a,lickValues_b);
    delayMicroseconds(loopDelta);
    curState=lookForSerialState();
  }

}

// ---------- Helper Functions


int lookForSerialState(){
  int pyState;
  if(Serial.available()>0){
    pyState=Serial.read();
    lastState=pyState;
    stateChange=1;
  }
  else if(Serial.available()<=0){
    pyState=lastState;
    stateChange=0;
  }
  return pyState;
}

int pollOpticalMouse() {
//  currentPosDelta=128;
  if(mpSerial.available()>0){
    currentPosDelta=mpSerial.parseInt();
  }
  else if(mpSerial.available()<=0){
    currentPosDelta=128;
  }  
}

int spitData(unsigned long d1,unsigned long d2,int d3, int d4, int d5, int d6){
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




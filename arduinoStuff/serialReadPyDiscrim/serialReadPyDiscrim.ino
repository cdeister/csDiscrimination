/*
 * See how they run
 * Three blind mice
 */

// I could do states with switch, but seems unecessary.
// I assume switch is more efficient http://www.blackwasp.co.uk/SpeedTestIfElseSwitch.aspx
// However, seems like it is negligible

#include <hidboot.h>
#include <usbhub.h>

int loopDelta=5;
int cueDuration=1000;
int pulseDur=40;
int delayDur_1=200;
int delayDur_2=20;
int cueDelay=500;
int toneDelay=2000;

unsigned long msOffset;
unsigned long msCorrected;
unsigned long cueTime;
unsigned long pulseTime;
unsigned long delayTime;
unsigned long ofs1;
unsigned long ofs2;
unsigned long ofs3;

int lastState;
int curState;

int deltaX=0;
int deltaY=0;
long posX=0;
long posY=0;

bool stateChange=0;
bool cueFired=0;
bool toneFired=0;
bool inPulse=1;
bool cueInit=0;

const int posPin=3;       // Engage Postive Reinforcment
const int negPin=4;       // Engage Aversive Reinforcment
const int waterPin=5;     // Engage Water
const int cueLED=13;
const int tonePin=53;
int sensorPin = A0;
int sensorValue = 0;

// ********** mouse class
class MouseRptParser : public MouseReportParser
{
protected:
  void OnMouseMove  (MOUSEINFO *mi);
};

void MouseRptParser::OnMouseMove(MOUSEINFO *mi){
    deltaX=(mi->dX);
    deltaY=(mi->dY);
    posX=posX+deltaX;
    posY=posY+deltaY;
};

USB Usb;
USBHub Hub(&Usb);
HIDBoot<HID_PROTOCOL_MOUSE> HidMouse(&Usb);
MouseRptParser  Prs;

// ************** end mouse


void setup() {
  pinMode(posPin, OUTPUT);
  pinMode(negPin, OUTPUT);
  pinMode(waterPin, OUTPUT);
  pinMode(tonePin, OUTPUT);
  pinMode(cueLED, OUTPUT);

  Serial.begin(9600); // initialize Serial communication
  while (!Serial);    // wait for the serial port to open
  Serial.println("Start");
  if (Usb.Init() == -1)
    Serial.println("OSC did not start.");
  delay(500);
  HidMouse.SetReportParser(0,(HIDReportParser*)&Prs);
  msOffset=millis();
}

void loop() {
  Usb.Task();
  // State Entry Housekeeping
  // These are things we want to happen when there is a state change.
  // currently position and time will reset.
  if(stateChange){
    posX=0;
    posY=0;
    msOffset=millis();
    digitalWrite(negPin,LOW);
    digitalWrite(posPin,LOW);
    digitalWrite(waterPin,LOW);
    digitalWrite(tonePin,LOW);
    digitalWrite(cueLED,LOW);
    cueFired=0;
    toneFired=0;
    inPulse=1;
    cueInit=0;
  }

  // SO: Initialization State
  // This is just a state that ensures that the arduino lets python know 
  // it is ready to spit out real data and not garbage
  if(curState==0){
    msOffset=millis();  // Reset time because this is technically the begining of the task
    Serial.print(String("data,0,0,0,0"));
    Serial.println();
    delay(loopDelta);
    curState=lookForSerialState();
  }


  // S1: Trial wait state.
  else if(curState==1){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S2: Trial initiation state.
  else if(curState==2){
    noTone(tonePin);
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S3: Sensory Task #1 Cue
  else if(curState==3){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    if(msCorrected>=cueDelay && cueFired==0){
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
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }
  
  // S4: Sensory Task #2 Cue
  else if(curState==4){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    if(msCorrected>=cueDelay && cueFired==0){
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
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }
  
  // S5: Sensory High
  else if(curState==5){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    tone(tonePin, 900, 1000);
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S6: Sensory Low
  else if(curState==6){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    tone(tonePin, 100, 1000);
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }

    // S7: Sensory High
  else if(curState==7){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    tone(tonePin, 900, 1000);
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S8: Sensory Low
  else if(curState==8){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    tone(tonePin, 100, 1000);
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
    curState=lookForSerialState();
  }
  else {
    noTone(tonePin);
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    sensorValue = analogRead(sensorPin);
    spitData(msCorrected,posX,curState,sensorValue);
    delay(loopDelta);
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

int spitData(int d1,int d2,int d3, int d4){
  Serial.print("data,");
  Serial.print(d1);
  Serial.print(',');
  Serial.print(d2);
  Serial.print(',');
  Serial.print(d3);
  Serial.print(',');
  Serial.print(d4);
  Serial.println();
}
//----------------------- 




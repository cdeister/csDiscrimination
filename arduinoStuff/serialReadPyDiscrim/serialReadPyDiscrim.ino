/*
 * See how they run
 * Three blind mice
 */

// I could do states with switch, but seems unecessary.
// I assume switch is more efficient http://www.blackwasp.co.uk/SpeedTestIfElseSwitch.aspx
// However, seems like it is negligible

#include <hidboot.h>
#include <usbhub.h>


unsigned long msOffset;
unsigned long msCorrected;
int lastState;
int curState;
int txBit;
int deltaX=0;
int deltaY=0;
long posX=0;
long posY=0;
int stateChange=0;
int loopDelta=5;

const int posPin=3;     // Engage Postive Reinforcment
const int negPin=4;    // Engage Aversive Reinforcment
const int waterPin=5;       // Engage Water
const int ledPin=13;        // Cue LED Pin


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

USB     Usb;
USBHub     Hub(&Usb);
HIDBoot<HID_PROTOCOL_MOUSE>    HidMouse(&Usb);
MouseRptParser  Prs;

// ************** end mouse


void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(posPin, OUTPUT);
  pinMode(negPin, OUTPUT);
  pinMode(waterPin, OUTPUT);

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
    digitalWrite(ledPin,LOW);
  }

  // SO: Initialization State
  // This is just a state that ensures that the arduino lets python know 
  // it is ready to spit out real data and not garbage
  if(curState==0){
    msOffset=millis();  // Reset time because this is technically the begining of the task
    Serial.print(String("data,0,0,0"));
    Serial.println();
    delay(loopDelta);
    curState=lookForSerialState();
  }


  // S1: Trial wait state.
 else if(curState==1){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    spitData(msCorrected,posX,curState);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S2: Trial initiation state.
  else if(curState==2){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    spitData(msCorrected,posX,curState);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S3: Engage Sensory Task 1
  else if(curState==3){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    spitData(msCorrected,posX,curState);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S4: Engage Sensory Task 2
  else if(curState==4){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    spitData(msCorrected,posX,curState);
    delay(loopDelta);
    curState=lookForSerialState();
  }

  // S5: Postive Outcome
  else if(curState==5){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    spitData(msCorrected,posX,curState);
    curState=lookForSerialState();
  }

  // S6: Negative Outcome
  else if(curState==6){
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    spitData(msCorrected,posX,curState);
    delay(loopDelta);
    curState=lookForSerialState();
  }
  
  else {
    // timestamp, dump data, check state
    msCorrected=millis()-msOffset;
    spitData(msCorrected,posX,curState);
    delay(loopDelta);
    curState=lookForSerialState();
  }

}

// ---------- Helper Functions


int lookForSerialState(){
  int pyState;
  if(Serial.available()>0){
    pyState=(Serial.read())-48;
    lastState=pyState;
    stateChange=1;
  }
  else if(Serial.available()<=0){
    pyState=lastState;
    stateChange=0;
  }
  return pyState;
}

int spitData(int d1,int d2,int d3){
  Serial.print("data,");
  Serial.print(d1);
  Serial.print(',');
  Serial.print(d2);
  Serial.print(',');
  Serial.print(d3);
  Serial.println();
}

//int blinkLights(int bDelta, int lPin, int bTime){
//  digitalWrite(lPin,HIGH);
//  bState=1;
//  bIt=1;
//  start=millis();
//  while bIt
//  
//}

//----------------------- 




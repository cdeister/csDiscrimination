/*
 * See how they run
 * Three blind mice
 */

#include <hidboot.h>
#include <usbhub.h>


unsigned long msOffset;
int lastState;
int curState;
int txBit;
int deltaX=0;
int deltaY=0;
long posX=0;
long posY=0;
int stateChange=0;
int sDelta=100;

const int ledPin=13; // pin to use for the Blue Cue LED


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
  // Initialization State == 0
  
if(curState==0){
  curState=lookForSerialState();
  Serial.print(String("data,0,0,0"));
  Serial.println();
  digitalWrite(ledPin, HIGH);
  delay(sDelta);
}

if(stateChange){
  posX=0;
  posY=0;
  //msOffset=millis();
}



if(curState==6){
  digitalWrite(ledPin, HIGH);

  // timestamp
  unsigned long msCurrent;
  unsigned long msCorrected;
  msCurrent=millis();
  msCorrected=msCurrent-msOffset;
 

  // dump data
  Serial.print("data,");
  Serial.print(msCorrected);
  Serial.print(',');
  Serial.print(posX);
  Serial.print(',');
  Serial.print(curState);
  Serial.println();
  delay(sDelta);
  // check state
  curState=lookForSerialState();
}

if(curState!=0 || curState !=6){
  digitalWrite(ledPin, LOW);

  // timestamp
  unsigned long msCurrent;
  unsigned long msCorrected;
  msCurrent=millis();
  msCorrected=msCurrent-msOffset;
 

  // dump data
  Serial.print("data,");
  Serial.print(msCorrected);
  Serial.print(',');
  Serial.print(posX);
  Serial.print(',');
  Serial.print(curState);
  Serial.println();
  delay(sDelta);
  // check state
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

//int blinkLight(freq,pin){
//  
//}
//}


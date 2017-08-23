/* csCueLights
  Drives an RGB neopixel array via serial reads.
  
  v1.0
  cdeister@brown.edu

*/

#include <Adafruit_GFX.h>
#include <Adafruit_NeoMatrix.h>
#include <Adafruit_NeoPixel.h>
#ifndef PSTR
#define PSTR // Make Arduino Due happy
#endif


#define PIN 6


int pulseDur = 10;
int delayDur = 100;
int inPulse = 1;
int sC;
int cueState = 5;
int lastCueState = 5;
boolean newData = false;
const byte numChars = 32;
char receivedChars[numChars];

bool blinkHeaderToggle = 0;
unsigned long pulseTimer;
unsigned long pulseOffset;
bool tLatch = 0;
int stateDelta = 0;


// Example for NeoPixel Shield.  In this application we'd like to use it
// as a 5x8 tall matrix, with the USB port positioned at the top of the
// Arduino.  When held that way, the first pixel is at the top right, and
// lines are arranged in columns, progressive order.  The shield uses
// 800 KHz (v2) pixels that expect GRB color data.
Adafruit_NeoMatrix matrix = Adafruit_NeoMatrix(4, 8, PIN,
                            NEO_MATRIX_TOP     + NEO_MATRIX_RIGHT +
                            NEO_MATRIX_COLUMNS + NEO_MATRIX_PROGRESSIVE,
                            NEO_GRB            + NEO_KHZ800);

const uint16_t colors[] = {
  matrix.Color(255, 0, 0), matrix.Color(0, 255, 0), matrix.Color(255, 0, 255)
};

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  matrix.begin();
  matrix.setBrightness(5);
  matrix.fillScreen(matrix.Color(0, 0, 255));
  matrix.show();
  delay(500); //debug
}


void loop() {
  flagReceive('c', '$');
  showSetNewData();
  checkStateChange();

  if (cueState == 2) {
    if (tLatch == 0) {
      matrix.fillScreen(matrix.Color(0, 255, 0));
      matrix.show();
      tLatch = 1;
    }
  }
  else if (cueState == 3) {
    if (tLatch == 0) {
      blinkHeaderToggle = 0;
      inPulse = 1;
      tLatch = 1;
    }
    else if (tLatch == 1) {
      nonBlockBlink(10, 200,matrix.Color(0, 0, 255));
    }
  }
  else if (cueState == 4) {
    if (tLatch == 0) {
      blinkHeaderToggle = 0;
      inPulse = 1;
      tLatch = 1;
    }
    else if (tLatch == 1) {
      nonBlockBlink(10, 50,matrix.Color(0, 0, 255));
    }
  }
  else if (cueState == 24) {
    if (tLatch == 0) {
      matrix.fillScreen(matrix.Color(255, 0, 255));
      matrix.show();
      tLatch = 1;
    }
    else if (tLatch == 1) {
      nonBlockBlink(100, 100, matrix.Color(255, 0, 255));
    }
  }
  else  {
    if (tLatch == 0) {
      matrix.fillScreen(matrix.Color(255, 0, 0));
      matrix.show();
      tLatch = 1;
    }
  }
}



void nonBlockBlink(int pDur, int dDur,const uint16_t pCol) {
  if (inPulse == 1) {
    if (blinkHeaderToggle == 0) {
      pulseOffset = millis();
      matrix.fillScreen(pCol);
      matrix.show();
      pulseTimer = millis() - pulseOffset;
      blinkHeaderToggle = 1;
    }
    else if (blinkHeaderToggle == 1 && pulseTimer <= pDur) {
      pulseTimer = millis() - pulseOffset;
    }
    else if (blinkHeaderToggle == 1 && pulseTimer > pDur){
      blinkHeaderToggle = 0;
      inPulse = 0;
    }
  }

  else if (inPulse == 0) {
    if (blinkHeaderToggle == 0) {
      pulseOffset = millis();
      matrix.fillScreen(0);
      matrix.show();
      pulseTimer = millis() - pulseOffset;
      blinkHeaderToggle = 1;
    }
    else if (blinkHeaderToggle == 1 && pulseTimer <= dDur) {
      pulseTimer = millis() - pulseOffset;
    }
    else if (blinkHeaderToggle == 1 && pulseTimer > dDur){
      blinkHeaderToggle = 0;
      inPulse = 1;
    }
  }
}

void flagReceive(char startChars, char endChars) {
  static boolean recvInProgress = false;
  static byte ndx = 0; char startMarker = startChars;
  char endMarker = endChars; char rc;

  while (Serial1.available() > 0 && newData == false) {
    rc = Serial1.read();

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

void showSetNewData() {
  if (newData == true) {
    cueState = int(String(receivedChars).toInt());
    newData = false;
  }
}

void checkStateChange() {
  stateDelta = abs(cueState - lastCueState);
  if (stateDelta != 0) {
    tLatch = 0;
    lastCueState = cueState;
  }
}







/* csCueLights
  Drives an RGB neopixel array via triggers.
  Early version, very messy.

  v0.5
  cdeister@brown.edu

*/

#include <Adafruit_GFX.h>
#include <Adafruit_NeoMatrix.h>
#include <Adafruit_NeoPixel.h>
#ifndef PSTR
#define PSTR // Make Arduino Due happy
#endif

#define PIN 6
#define cue1Pin 12
#define cue2Pin 11
#define initPin 10
#define toPin 5


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

bool cue1_trig;
bool cue2_trig;
bool to_trig;
bool canInitiate_trig;
bool ranHeader = 0;
int sC;
int inPulse;

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
  pinMode(cue1Pin, INPUT);
  pinMode(cue2Pin, INPUT);
  pinMode(initPin, INPUT);
  pinMode(toPin, INPUT);
  matrix.begin();
  matrix.setBrightness(20);
  matrix.fillScreen(matrix.Color(255, 0, 0));
  matrix.show();
  delay(500); //debug
}


void loop() {
  cue1_trig = digitalRead(cue1Pin);
  cue2_trig = digitalRead(cue2Pin);
  canInitiate_trig = digitalRead(initPin);
  to_trig = digitalRead(toPin);


  if (cue1_trig) {
    sC = 1;
  }
  else if (cue2_trig) {
    sC = 2;
  }
  else if (canInitiate_trig) {
    sC = 3;
  }
  else if (to_trig) {
    sC = 4;
  }
  else  {
    sC = 5;
  }

    Serial.print(sC);
    Serial.print(',');
    Serial.print(ranHeader);
    Serial.print(',');
    Serial.println(inPulse);

  switch (sC) {
    case 1:
      nonBlockBlink(50000, 50000, 1, matrix.Color(255, 0, 255));
      break;

    case 2:
      nonBlockBlink(50000, 50000, 1, matrix.Color(255, 0, 255));
      break;
    case 3:
      matrix.fillScreen(matrix.Color(0, 255, 0));
      matrix.show();
      break;
    case 4:
      nonBlockBlink(50000, 50000, 1, matrix.Color(255, 0, 255));
      break;
    case 5:
      matrix.fillScreen(0);
      matrix.show();
      break;

    default:
      matrix.fillScreen(0);
      matrix.show();
  }
}


void nonBlockBlink(int pT, int dT, int startOnOrOff, const uint16_t col) {
  pulseTime = micros() - pulseOffset;
  delayTime = micros() - delayOffset;
  Serial.print(pulseTime);
  Serial.print(',');
  Serial.println(delayTime);
  if (inPulse == 1) {
    delayOffset = micros();
    if (pulseTime <= pT) {
      matrix.fillScreen(col);
      matrix.show();
    }
    else if (pulseTime > pT) {
      delayOffset = micros();
      matrix.fillScreen(0);
      matrix.show();
      inPulse = 0;
    }
  }

  else if (inPulse == 0) {
    pulseOffset = micros();
    if (delayTime <= dT) {
      matrix.fillScreen(0);
      matrix.show();
    }
    else if (delayTime > dT) {
      pulseOffset = micros();
      inPulse = 1;
    }
  }
}






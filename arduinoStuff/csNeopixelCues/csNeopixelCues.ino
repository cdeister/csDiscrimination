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
#define cue1Pin 13
#define cue2Pin 12
#define initPin 10
#define toPin 5




bool iPinOn;
bool c1PinOn;
bool c2PinOn;
bool toPinOn;


int pulseDur = 10;
int delayDur = 100;
int inPulse = 1;
int sC;


bool blinkHeaderToggle = 0;
unsigned long pulseTimer;
unsigned long pulseOffset;






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
  c1PinOn = digitalRead(cue1Pin);
  c2PinOn = digitalRead(cue2Pin);
  iPinOn = digitalRead(initPin);
  toPinOn = digitalRead(toPin);


  if (c1PinOn) {
    sC = 1;
    nonBlockBlink(20, 300, matrix.Color(0, 0, 255));
  }
  else if (c2PinOn) {
    sC = 2;
    nonBlockBlink(20, 90, matrix.Color(0, 0, 255));
  }
  else if (iPinOn) {
    sC = 3;
    matrix.fillScreen(matrix.Color(0, 255, 0));
    matrix.show();
  }
  else if (toPinOn) {
    sC = 4;
    nonBlockBlink(200, 200, matrix.Color(255, 0, 255));
  }
  else  {
    sC = 5; // off
    matrix.fillScreen(matrix.Color(255, 0, 0));
    matrix.show();
  }
  Serial.println(sC);

}





void nonBlockBlink(int pDur, int dDur, const uint16_t col) {
  if (inPulse == 1) {
    if (blinkHeaderToggle == 0) {
      pulseOffset = millis();
      matrix.fillScreen(col);
      matrix.show();
      pulseTimer = millis() - pulseOffset;
      Serial.println("pulse header");
      blinkHeaderToggle = 1;
    }
    else if (pulseTimer <= pDur) {
      pulseTimer = millis() - pulseOffset;
      Serial.println("pulseTimer");
    }
    else {
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
      Serial.println("delay header");
      blinkHeaderToggle = 1;
    }
    else if (pulseTimer <= dDur) {
      pulseTimer = millis() - pulseOffset;
    }
    else {
      blinkHeaderToggle = 0;
      inPulse = 1;
    }
  }
}






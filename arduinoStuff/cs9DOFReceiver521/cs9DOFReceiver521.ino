/*
 cs9DOFReceiver
 This script renders a nordic 521 based MC into a UART peripheral that will connect to a conigured central.
 I put this on an adafruit m0 bluefruit feather. The 32u based board works too. 
 The 522 board is not ideal, because it is difficult to configure hardware serial (it's non-existent). 

 v1.0 -- 
 cdeister@brown.edu
 
 */


#include <SPI.h>
#include <Wire.h>


#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"
#include "BluefruitConfig.h"


Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_CS, BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);

#define PIN             30   /* Pin used to drive the NeoPixels */
#define MATRIX_WIDTH    4
#define MATRIX_HEIGHT   8
#define MATRIX_LAYOUT   (NEO_MATRIX_TOP + NEO_MATRIX_RIGHT + NEO_MATRIX_COLUMNS + NEO_MATRIX_PROGRESSIVE)



unsigned long lastTime;
String readOrient="0";
int lastOrient = 0;
int orientDelta = 0;
int numRevs = 0;
bool blinkLights = 0;
bool useOLED = 1;
int uptCntr = 0;
int updateInt = 50;

const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;


void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);



  if ( !ble.begin(VERBOSE_MODE) ) {
    //    Serial.println(F("Couldn't find Bluefruit"));
  }

  ble.echo(false);
  ble.info();
  delay(100);
  ble.setMode(BLUEFRUIT_MODE_DATA);
  ble.verbose(false);  // debug info is a little annoying after this point!
  lastTime = millis();
}

void loop(void) {
  lastTime = millis();
  while (ble.isConnected() == 0) {

    Serial.print(101);
    Serial.print(',');
    Serial.println(-10);
    Serial1.write(101);
    Serial1.write(',');
    Serial1.write(-10);
    Serial1.write('\n');
    delay(100);
  }

  while (ble.isConnected()) {
    flagReceive('o', '>');
    showNewData();
    delayMicroseconds(50);
  }
}

void flagReceive(char startChars, char endChars) {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = startChars;
  char endMarker = endChars;
  char rc;

  while (ble.available() > 0 && newData == false) {
    rc = ble.read();

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

void showNewData() {
  if (newData == true) {
    readOrient = String(receivedChars);
    newData = false;
  }
  Serial1.print('o');
  Serial1.print(readOrient);
  Serial1.print('>');
  Serial1.print('\n');
  Serial.print(readOrient);
  Serial.print('\n');

}




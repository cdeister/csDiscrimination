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

//#include <Adafruit_GFX.h>
//#include <Adafruit_SSD1306.h>
//Adafruit_SSD1306 display = Adafruit_SSD1306();
//#if defined(ESP8266)
//#define BUTTON_A 0
//#define BUTTON_B 16
//#define BUTTON_C 2
//#define LED      0
//#elif defined(ESP32)
//#define BUTTON_A 15
//#define BUTTON_B 32
//#define BUTTON_C 14
//#define LED      13
//#elif defined(ARDUINO_STM32F2_FEATHER)
//#define BUTTON_A PA15
//#define BUTTON_B PC7
//#define BUTTON_C PC5
//#define LED PB5
//#elif defined(TEENSYDUINO)
//#define BUTTON_A 4
//#define BUTTON_B 3
//#define BUTTON_C 8
//#define LED 13
//#elif defined(ARDUINO_FEATHER52)
//#define BUTTON_A 31
//#define BUTTON_B 30
//#define BUTTON_C 27
//#define LED 17
//#else // 32u4, M0, and 328p
//#define BUTTON_A 9
//#define BUTTON_B 6
//#define BUTTON_C 5
//#define LED      13
//#endif
//
//#if (SSD1306_LCDHEIGHT != 32)
//#error("Height incorrect, please fix Adafruit_SSD1306.h!");
//#endif


#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"
#include "BluefruitConfig.h"


Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_CS, BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);


unsigned long lastTime;
String readOrient = "0";
int lastOrient = 0;
int orientDelta = 0;
int numRevs = 0;
bool blinkLights = 0;
//bool useOLED = 0;
//int uptCntr = 0;
//int updateInt = 50;

const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;


void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);

  //  if (useOLED == 1) {
  //    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);  // initialize with the I2C addr 0x3C (for the 128x32)
  //    pinMode(BUTTON_A, INPUT_PULLUP);
  //    pinMode(BUTTON_B, INPUT_PULLUP);
  //    pinMode(BUTTON_C, INPUT_PULLUP);
  //    display.display();
  //    delay(500);
  //    display.clearDisplay();
  //    display.display();
  //    display.setTextSize(2);
  //    display.setTextColor(WHITE);
  //    display.setCursor(0, 0);
  //    display.println("no bt");
  //    display.setCursor(0, 0);
  //    display.display(); // actually display all of the above
  //  }

  if ( !ble.begin(VERBOSE_MODE) ) {
    //    Serial.println(F("Couldn't find Bluefruit"));
  }

  ble.echo(false);
  ble.info();
  delay(100);
  ble.setMode(BLUEFRUIT_MODE_DATA);
  ble.verbose(false);  // debug info is a little annoying after this point!
  lastTime = micros();
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
    //    if (useOLED == 1) {
    //      uptCntr++;
    //      if (uptCntr > updateInt) {
    //        display.clearDisplay();
    //        display.setCursor(0, 0);
    //        display.println("no bt yet");
    //        display.setCursor(0, 0);
    //        display.display(); // actually display all of the above
    //        uptCntr = 0;
    //      }
    //    }
  }

  while (ble.isConnected()) {
    flagReceive('o', '>');
    showNewData();
    delayMicroseconds(50);
    //    if (useOLED == 1) {
    //      uptCntr++;
    //      if (uptCntr > updateInt) {
    //        display.clearDisplay();
    //        display.setCursor(0, 0);
    //        display.println(readOrient);
    //        display.setCursor(0, 0);
    //        display.display(); // actually display all of the above
    //        uptCntr = 0;
    //      }
    //    }
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




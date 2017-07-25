#include <Wire.h>
#include "Adafruit_VL6180X.h"

#define hwSer Serial1

Adafruit_VL6180X vl = Adafruit_VL6180X();

int lastRange;
int curRange;

void setup() {
  Serial.begin(9600);
  hwSer.begin(115200);

  // wait for serial port to open on native usb devices
  while (!Serial) {
    delay(1);
  }

  Serial.println("Adafruit VL6180x test!");
  if (! vl.begin()) {
    Serial.println("Failed to find sensor");
    while (1);
  }
  Serial.println("Sensor found!");
}

void loop() {
  float lux = vl.readLux(VL6180X_ALS_GAIN_5);
  uint8_t range = vl.readRange();
  uint8_t status = vl.readRangeStatus();

  if (status == VL6180X_ERROR_NONE) {
    curRange = range;
  }
  else if (status != VL6180X_ERROR_NONE){
    curRange=lastRange;  //redundant but readable
  }

//  Serial.print("lidar: ");
//  Serial.print(lux);
//  Serial.print(",");
//  Serial.print(curRange);
//  Serial.print(",");
  hwSer.println(curRange);
  lastRange=curRange;


  delayMicroseconds(100);
}

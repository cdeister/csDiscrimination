#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM9DS0.h>
#include <Adafruit_Simple_AHRS.h>

Adafruit_LSM9DS0     lsm(1000);  // Use I2C, ID #1000
Adafruit_Simple_AHRS ahrs(&lsm.getAccel(), &lsm.getMag());

#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"
#include "BluefruitConfig.h"


int curRoll = 0;
int lastRoll = 0;

Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_CS, BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);

// Call this to calibrate
void configureLSM9DS0() {
  // 1.) Set the accelerometer range
  lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_2G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_4G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_6G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_8G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_16G);

  // 2.) Set the magnetometer sensitivity
  lsm.setupMag(lsm.LSM9DS0_MAGGAIN_2GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_4GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_8GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_12GAUSS);

  // 3.) Setup the gyroscope
  lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_245DPS);
  //lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_500DPS);
  //lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_2000DPS);
}

void setup()
{

  Serial.begin(115200);
  if (!lsm.begin())
  {
    Serial.print(F("Ooops, no LSM9DS0 detected ... Check your wiring or I2C ADDR!"));
    while (1);
  }

  if ( !ble.begin(VERBOSE_MODE) )
  {
    //    Serial.println(F("Couldn't find Bluefruit"));
  }

  ble.echo(false);
  ble.info();
  delay(100);
  ble.setMode(BLUEFRUIT_MODE_DATA);
  ble.verbose(false);  // debug info is a little annoying after this point!


}

void loop(void)
{
  while (ble.isConnected() == 0) {

    sensors_vec_t   orientation;

    if (ahrs.getOrientation(&orientation)) {
      curRoll = int(orientation.roll);
    }
    else if (ahrs.getOrientation(&orientation) == 0) {
      curRoll = lastRoll;
    }
    Serial.print('o');
    Serial.print(curRoll);
    Serial.println('>');
    lastRoll = curRoll;

    delayMicroseconds(500);
  }

  while (ble.isConnected()) {
    sensors_vec_t   orientation;

    if (ahrs.getOrientation(&orientation)) {
      curRoll = int(orientation.roll);
    }
    else if (ahrs.getOrientation(&orientation) == 0) {
      curRoll = lastRoll;
    }
    ble.print('o');
    ble.print(curRoll);
    ble.println('>');

    Serial.print('o');
    Serial.print(curRoll);
    Serial.println('>');

    lastRoll = curRoll;

    delayMicroseconds(100);
  }
}




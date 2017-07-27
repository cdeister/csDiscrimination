/* 
 cs9DOFStreamer
 Wireless orientation tracking.
 Configured here for tracking one orientation for a mouse wheel tracker.
 Makes use of adafruit's i2c and blueart libraries. Also, as all BLE, makes use of nordic semis API. 
 This script is loaded onto a nrf522 based board. 
 It has to be an nrf522 board and not 521 so it can act as a client and connect to a uart target.
 I place an adafruit nrf522 feather in the underside of a wheel. This is connected to a 9DOF sensor. 
 I like the LSM9DS0 9DOF, this script uses adafruit's AHRS library that fuses the 9DOFs together. 
 There are other chips that do on chip fusion.
 
 v1.0
 cdeister@brown.edu
 
*/

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM9DS0.h>
#include <Adafruit_Simple_AHRS.h>

#include <bluefruit.h>
BLEClientDis  clientDis;
BLEClientUart clientUart;

Adafruit_LSM9DS0     lsm(1000);  // Use I2C, ID #1000
Adafruit_Simple_AHRS ahrs(&lsm.getAccel(), &lsm.getMag());

int curOrient = 0;
int curRoll = 0;
int curPitch = 0;
int curHead = 0;
int orientDelta = 0;

int lastOrient = 0;
int lastRoll = 0;
int lastPitch = 0;
int lastHead = 0;

unsigned long lastTime;


void configureLSM9DS0(void) {
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


void setup() {
  Serial.begin(115200);
  if (!lsm.begin())
  {
    Serial.print(F("Ooops, no LSM9DS0 detected ... Check your wiring or I2C ADDR!"));
    while (1);
  }
  configureLSM9DS0();


  Bluefruit.begin(false, true);
  Bluefruit.setName("Wheel1");
  clientDis.begin();
  clientUart.begin();
  Bluefruit.setConnLedInterval(5);
Bluefruit.autoConnLed(1);

  Bluefruit.Central.setConnectCallback(connect_callback);
  Bluefruit.Central.setDisconnectCallback(disconnect_callback);

  Bluefruit.Central.setScanCallback(scan_callback);
  Bluefruit.Central.startScanning();
  lastTime = millis();
}


void scan_callback(ble_gap_evt_adv_report_t* report) {
  if ( Bluefruit.Central.checkUuidInScan(report, BLEUART_UUID_SERVICE)) {
    Bluefruit.Central.connect(report);
  }
}


void connect_callback(uint16_t conn_handle){
  Serial.println("Connected");
  if ( clientDis.discover(conn_handle)) {
    Serial.println("Found it");
    char buffer[32 + 1];
    memset(buffer, 0, sizeof(buffer));
    if ( clientDis.getManufacturer(buffer, sizeof(buffer))) {
      Serial.print("Manufacturer: ");
      Serial.println(buffer);
    }

    memset(buffer, 0, sizeof(buffer));
    if ( clientDis.getModel(buffer, sizeof(buffer))) {
      Serial.print("Model: ");
      Serial.println(buffer);
    }
    Serial.println();
  }

  Serial.print("Discovering BLE Uart Service ... ");

  if (clientUart.discover(conn_handle)) {
    Serial.println("Found it");
    Serial.println("Enable TXD's notify");
    clientUart.enableTXD();
    Serial.println("Ready to receive from peripheral");
  } else {
    Serial.println("Found NONE");
  }
}


void disconnect_callback(uint16_t conn_handle, uint8_t reason)
{
  (void) conn_handle;
  (void) reason;

  Serial.println("Disconnected");
  Serial.println("Bluefruit will auto start scanning (default)");
}

void uart_rx_callback(void) {

}
int pass = 0;

void loop() {
  while (Bluefruit.Central.connected() == 0) {
    pollMotion();
    Serial.print('o');
    Serial.print(curRoll);
    Serial.println('>');
    delayMicroseconds(100);
  }

  while (Bluefruit.Central.connected()) {
    pollMotion();
    Serial.print('o');
    Serial.print(curRoll);
    Serial.println('>');
    delayMicroseconds(100);
    
    clientUart.print('o');
    clientUart.print(curRoll);
    clientUart.println('>');

    delayMicroseconds(100);
  }
}

void pollMotion() {
  sensors_vec_t   orientation;
  if (ahrs.getOrientation(&orientation)) {
    curRoll=orientation.roll;
    curPitch=orientation.pitch;
    curHead=orientation.heading;
    
    lastRoll=curRoll;
    lastPitch=curPitch;
    lastHead=curHead;
  }
  else if (ahrs.getOrientation(&orientation) == 0) {
    curRoll=lastRoll;
    curPitch=lastPitch;
    curHead=lastHead;
  }
}


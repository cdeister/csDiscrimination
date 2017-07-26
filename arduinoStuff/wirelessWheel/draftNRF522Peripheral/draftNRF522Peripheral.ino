#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM9DS0.h>
#include <Adafruit_Simple_AHRS.h>

Adafruit_LSM9DS0     lsm(1000);  // Use I2C, ID #1000
Adafruit_Simple_AHRS ahrs(&lsm.getAccel(), &lsm.getMag());

#include <bluefruit.h>

BLEClientDis  clientDis;
BLEClientUart clientUart;

int readOrient;
int lastOrient = 0;
int curPitch = 0;
int lastPitch = 0;

int curRoll = 0;
int lastRoll = 0;
unsigned long lastTime;


const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;


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


  // Enable both peripheral and central
  Bluefruit.begin(true, false);
  Bluefruit.setName("Bluefruit52aa");
  clientDis.begin();
  clientUart.begin();
  //  clientUart.setRxCallback(uart_rx_callback);
  Bluefruit.setConnLedInterval(1);

  // Callbacks for Central
  Bluefruit.Central.setConnectCallback(connect_callback);
  Bluefruit.Central.setDisconnectCallback(disconnect_callback);

  // Start Central Scan
  Bluefruit.Central.setScanCallback(scan_callback);
  Bluefruit.Central.startScanning();
  lastTime = micros();
}


void scan_callback(ble_gap_evt_adv_report_t* report)
{
  // Check if advertising contain BleUart service
  if ( Bluefruit.Central.checkUuidInScan(report, BLEUART_UUID_SERVICE) )
  {
    // Connect to device with bleuart service in advertising
    // Use Min & Max Connection Interval default value
    Bluefruit.Central.connect(report);
  }
}

/**
   Callback invoked when an connection is established
   @param conn_handle
*/
void connect_callback(uint16_t conn_handle)
{
  Serial.println("Connected");

  //  Serial.print("Dicovering DIS ... ");
  if ( clientDis.discover(conn_handle) )
  {
    Serial.println("Found it");
    char buffer[32 + 1];

    // read and print out Manufacturer
    memset(buffer, 0, sizeof(buffer));
    if ( clientDis.getManufacturer(buffer, sizeof(buffer)) )
    {
      Serial.print("Manufacturer: ");
      Serial.println(buffer);
    }

    // read and print out Model Number
    memset(buffer, 0, sizeof(buffer));
    if ( clientDis.getModel(buffer, sizeof(buffer)) )
    {
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

void loop() {
  if ( Bluefruit.Peripheral.connected() == 0) {
    Serial.println

    sensors_vec_t   orientation;

    if (ahrs.getOrientation(&orientation)) {
      curRoll = int(orientation.roll);
      curPitch = int(orientation.pitch);
    }
    else if (ahrs.getOrientation(&orientation) == 0) {
      curRoll = lastRoll;
    }
    Serial.print('o');

    Serial.print(int(curRoll));
    Serial.println(">");
    lastRoll = curRoll;

    delayMicroseconds(1000);
  }
  else if ( Bluefruit.Central.connected() == 1) {

    sensors_vec_t   orientation;

    if (ahrs.getOrientation(&orientation)) {
      curRoll = int(orientation.roll);
      curPitch = int(orientation.pitch);
    }
    else if (ahrs.getOrientation(&orientation) == 0) {
      curRoll = lastRoll;
    }
    Serial.print('o');

    Serial.print(int(curRoll));
    Serial.println(">");
    lastRoll = curRoll;

    delayMicroseconds(100);
  }
}


void flagReceive(char startChars, char endChars) {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = startChars;
  char endMarker = endChars;
  char rc;

  while (clientUart.available() > 0 && newData == false) {
    rc = clientUart.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
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
    Serial.println(receivedChars);
    newData = false;
  }
}

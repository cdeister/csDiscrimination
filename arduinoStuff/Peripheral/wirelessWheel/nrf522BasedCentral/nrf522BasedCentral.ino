#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_GFX.h>
#include <Adafruit_NeoMatrix.h>
#include <bluefruit.h>

//#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_FeatherOLED.h>
Adafruit_FeatherOLED oled = Adafruit_FeatherOLED();

#define mserial Serial

#define PIN             30   /* Pin used to drive the NeoPixels */

#define MATRIX_WIDTH    4
#define MATRIX_HEIGHT   8
#define MATRIX_LAYOUT   (NEO_MATRIX_TOP + NEO_MATRIX_RIGHT + NEO_MATRIX_COLUMNS + NEO_MATRIX_PROGRESSIVE)

Adafruit_NeoMatrix matrix = Adafruit_NeoMatrix(MATRIX_WIDTH, MATRIX_HEIGHT, PIN,
                            MATRIX_LAYOUT,
                            NEO_GRB + NEO_KHZ800);

BLEClientDis  clientDis;
BLEClientUart clientUart;

unsigned long lastTime;
int readOrient=0;;
int lastOrient=0;
int orientDelta=0;
int numRevs=0;
bool blinkLights = 0;
bool useOLED = 1;
int uptCntr=0;

const byte numChars = 32;
char receivedChars[numChars];

boolean newData = false;

const uint16_t colors[] = {
  matrix.Color(255, 0, 0), matrix.Color(0, 255, 0), matrix.Color(0, 0, 255)
};


void setup()
{
  mserial.begin(115200);
  oled.init();
  oled.setBatteryVisible(true);


  matrix.begin();
  matrix.setTextWrap(false);
  matrix.setBrightness(1);
  matrix.setTextColor(colors[0]);
  matrix.fillScreen(colors[0]);
  matrix.show();
  matrix.fillScreen(0);
  matrix.show();

  // Enable both peripheral and central
  Bluefruit.begin(false, true);
  Bluefruit.setName("Bluefruit52");
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
  lastTime = millis();
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
  mserial.println("Connected");
  // Config Neopixels Matrix

  //  Serial.print("Dicovering DIS ... ");
  if ( clientDis.discover(conn_handle) )
  {
    mserial.println("Found it");
    char buffer[32 + 1];

    // read and print out Manufacturer
    memset(buffer, 0, sizeof(buffer));
    if ( clientDis.getManufacturer(buffer, sizeof(buffer)) )
    {
      mserial.print("Manufacturer: ");
      mserial.println(buffer);
    }

    // read and print out Model Number
    memset(buffer, 0, sizeof(buffer));
    if ( clientDis.getModel(buffer, sizeof(buffer)) )
    {
      mserial.print("Model: ");
      mserial.println(buffer);
    }

    mserial.println();
  }

  mserial.print("Discovering BLE Uart Service ... ");

  if (clientUart.discover(conn_handle)) {
    mserial.println("Found it");
    mserial.println("Enable TXD's notify");
    clientUart.enableTXD();
    mserial.println("Ready to receive from peripheral");
  } else {
    mserial.println("Found NONE");
  }
}


void disconnect_callback(uint16_t conn_handle, uint8_t reason)
{
  (void) conn_handle;
  (void) reason;

  mserial.println("Disconnected");
  mserial.println("Bluefruit will auto start scanning (default)");
}

void uart_rx_callback(void) {

}
int x  = matrix.width();
int pass = 0;

void loop() {
  lastTime = millis();
  while (Bluefruit.Central.connected() == 0) {
    oled.clearDisplay();
    oled.setBattery(0.00);
    oled.renderBattery();
    oled.print("waiting: ");
    oled.print(((millis() - lastTime) * 0.001) * 0.017);
    oled.println(" min");
    oled.display();
    
    mserial.print(101);
    mserial.print(',');
    mserial.print(-10);
    delay(100);

  }


  while ( Bluefruit.Central.connected()) {
    if (uptCntr>100){
      oled.clearDisplay();
      oled.setBattery(0.00);
      oled.renderBattery();
      oled.print(readOrient);
      oled.display();
      uptCntr=0;
    }
    flagReceive('o', '>');
    showNewData();
    uptCntr++;
    delayMicroseconds(100);
  }
}

//
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
      else if (rc == endMarker ){
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
    readOrient=int(String(receivedChars).toInt())+180;
    orientDelta=readOrient-lastOrient;
    lastOrient=readOrient;
    mserial.write(readOrient);
    mserial.write(',');
    mserial.write(orientDelta);
    mserial.write('\n');
    newData = false;
  }
}


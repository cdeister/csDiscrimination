#define capSerial Serial1

const int capSensA = 23;
const int capSensB = 15;

const int ledPin = 13;
int lickValA = 0;
int lickValB = 0;

unsigned long lastTime;

String sendAString;
String sendBString;
String aLabel = "A";
String bLabel = "B";
String lickAStr;
String lickBStr;


void setup() {
  Serial.begin(115200); // initialize Serial communication
  capSerial.begin(115200);
  lastTime = micros();
  pinMode(ledPin, OUTPUT);
}

void loop() {

  digitalWrite(ledPin, LOW);
  lickValA = touchRead(capSensA);
  digitalWrite(ledPin, LOW);
  lickValB = touchRead(capSensB);

  lickAStr = String(lickValA);
  lickBStr = String(lickValB);
  
    int padL = (5 - lickAStr.length());
    for (int i = 0; i < padL; i++) {
      lickAStr = String(0 + lickAStr);
    }
  
    padL = (5 - lickBStr.length());
    for (int i = 0; i < padL; i++) {
      lickBStr = String(0 + lickBStr);
    }

  sendAString = String('a' + lickAStr);
  sendBString = String('b' + lickBStr);



  Serial.println(sendAString);
  Serial.println(sendBString);

  capSerial.println(sendAString);
  capSerial.println(sendBString);


  digitalWrite(ledPin, HIGH);
  delayMicroseconds(100);
//  capSerial.flush();

}






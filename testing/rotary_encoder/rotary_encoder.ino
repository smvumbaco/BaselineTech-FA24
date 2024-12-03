//for Arduino testing:
const int PIN_CS = 4;     //blue
const int PIN_CLOCK = 6;  //yellow
const int PIN_DATA = 7;   //green 

//for ESP32: 
//#define PIN_CS 29       //blue
//#define PIN_CLOCK 28    //yellow
//#define PIN_DATA 27     //green 

void setup() {
  Serial.begin(115200);
  pinMode(PIN_CS, OUTPUT);
  pinMode(PIN_CLOCK, OUTPUT);
  pinMode(PIN_DATA, INPUT);

  digitalWrite(PIN_CLOCK, HIGH);
  digitalWrite(PIN_CS, LOW);
}

//byte stream[16];
void loop() {

  digitalWrite(PIN_CS, HIGH);       //CS must be driven high once to get data
  digitalWrite(PIN_CS, LOW);
  int pos = 0;
  for (int i=0; i<10; i++) {
    digitalWrite(PIN_CLOCK, LOW);   //get position data from bit corresponding to CLK signal 
    digitalWrite(PIN_CLOCK, HIGH);
   
    pos = pos | digitalRead(PIN_DATA);    //binary to int 
    if(i<9) pos = pos << 1;
  }
  for (int i=0; i<=6; i++) {         //parity/status bits, ignore 
    digitalWrite(PIN_CLOCK, LOW);
    digitalWrite(PIN_CLOCK, HIGH);
  }
  Serial.println(pos);
  delay(100);
}
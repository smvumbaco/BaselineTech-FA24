//EMS22A absolute binary non-contacting rotary encoder
//all hands example code 

const int PIN_CS = 4;     //blue
const int PIN_CLOCK = 6;  //yello
const int PIN_DATA = 7;   //green

void setup() {
  Serial.begin(115200);
  pinMode(PIN_CS, OUTPUT);        //set pins input/output
  pinMode(PIN_CLOCK, OUTPUT);
  pinMode(PIN_DATA, INPUT);

  digitalWrite(PIN_CLOCK, HIGH);
  digitalWrite(PIN_CS, LOW);
}


//byte stream[16];
void loop() {

  digitalWrite(PIN_CS, HIGH);
  digitalWrite(PIN_CS, LOW);
  int pos = 0;
  for (int i=0; i<10; i++) {
    digitalWrite(PIN_CLOCK, LOW);
    digitalWrite(PIN_CLOCK, HIGH);
   
    pos= pos | digitalRead(PIN_DATA);
    if(i<9) pos = pos << 1;             //binary input bit-wise to decimal
  }
  for (int i=0; i<6; i++) {             //drive clock to bypass status/parity bits
    digitalWrite(PIN_CLOCK, LOW);
    digitalWrite(PIN_CLOCK, HIGH);
  }
  digitalWrite(PIN_CLOCK, LOW);
  digitalWrite(PIN_CLOCK, HIGH);
  Serial.println(pos);
  delay(75);    //keep between 100 and 75 for displaying values 
}
/*
  AnalogReadSerial

  Reads an analog input on pin 0, prints the result to the Serial Monitor.
  Graphical representation is available using Serial Plotter (Tools > Serial Plotter menu).
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.

  This example code is in the public domain.

  https://www.arduino.cc/en/Tutorial/BuiltInExamples/AnalogReadSerial
*/

// the setup routine runs once when you press reset:
void setup() {
  pinMode(3, OUTPUT);
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

// the loop routine runs over and over again forever:
void loop(){
  float value, voltageA0, voltageA1;
  
  voltageA0=(float)analogRead(A0)*5/1023;
  voltageA1=(float)analogRead(A1)*5/1023;
  
  delay(100);

  digitalWrite(3, HIGH);
  delay(100);
  
  Serial.println(float(voltageA0-voltageA1));

  if(Serial.read() != -1){
    value = Serial.read();
  }  
}

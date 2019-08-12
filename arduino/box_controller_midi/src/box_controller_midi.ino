#include <Servo.h>
#include <usbmidi.h>

#define DEBUG_MODE false  // Debug mode links pot input to servo, should be false for normal use.

Servo servoObject;

#define SERVOPIN 10
#define POTPIN 0
#define POTMIN 170
#define POTMAX 852
#define SERVOMIN 5
#define SERVOMAX 175
#define MIDI_CONTROL    0b10110000

byte lastPotValue;
byte lastWrittenPotValue;
int goalPosition = 64;
int lastGoalPosition;
int servoCommand;
int rawPotValue;
byte potValue;

byte receivedPositionCommand = 0;

void sendCC(uint8_t channel, uint8_t control, uint8_t value) {
	USBMIDI.write(0xB0 | (channel & 0xf));
	USBMIDI.write(control & 0x7f);
	USBMIDI.write(value & 0x7f);
}

void setup()
{
  //Serial.begin(115200);
  servoObject.attach(SERVOPIN);
}

void loop()
{
  // Pot values.
  rawPotValue = constrain(analogRead(POTPIN), POTMIN, POTMAX);
  potValue = map(rawPotValue, POTMIN, POTMAX, 0, 127);
  // Handle Potentiometer
  if (abs(potValue - lastWrittenPotValue) > 0x01) {
    //Serial.write(potValue);
    //USBMIDI.write(0xB0 | (channel & 0xf)); // write 0xB (CC), 0x0 (channel 0)
    USBMIDI.write(0xB0); // write 0xB (CC), 0x0 (channel 0)
    USBMIDI.write(0 & 0x7f); // write control 0
    USBMIDI.write(potValue & 0x7f); // write CC value
    lastWrittenPotValue = potValue;
    USBMIDI.flush();
  }
  lastPotValue = potValue;

  // Only write if values have changed.
  // Handle Servo
  // while (Serial.available() > 0) {
  // MIDI
  USBMIDI.poll();
  while (USBMIDI.available()) {
    //Parse MIDI
    u8 command=0, channel=0, cc_number=0, cc_value=0;
    while(!(USBMIDI.peek() & 0b10000000)) USBMIDI.read();
    //goalPosition = Serial.read(); 
    command = USBMIDI.read();
    channel = (command & 0b00001111)+1;
    command = command & 0b11110000;

    switch(command) {
      case MIDI_CONTROL:
        cc_number = USBMIDI.read();
        cc_value = USBMIDI.read();
        goalPosition = cc_value;
        //if(USBMIDI.peek() & 0b10000000) continue; 
        //if(USBMIDI.peek() & 0b10000000) continue; 
        break;
    }
  }
  if (abs(goalPosition - lastGoalPosition) > 2) {
    commandServo(goalPosition);
    lastGoalPosition = goalPosition;
  }

}

/// Move the servo in response to input bytes
void commandServo(byte goal)
{
  servoCommand = constrain(map(goal, 0, 127, SERVOMIN, SERVOMAX), SERVOMIN, SERVOMAX);
  servoObject.write(servoCommand);
}


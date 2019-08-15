#include <Servo.h>
#include "MIDIUSB.h"

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

void setup()
{
  Serial.begin(115200);
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
    // USBMIDI.write(0xB0); // write 0xB (CC), 0x0 (channel 0)
    // USBMIDI.write(0 & 0x7f); // write control 0c
    // USBMIDI.write(potValue & 0x7f); // write CC value
    midiEventPacket_t event = {0x0B, 0xB0 | 0x0, 0x0, potValue & 0x7f};
    MidiUSB.sendMIDI(event);
    lastWrittenPotValue = potValue;
    MidiUSB.flush();
  }
  lastPotValue = potValue;

  // Only write if values have changed.
  // Handle Servo
  // while (Serial.available() > 0) {
  // MIDI
  midiEventPacket_t rx;
  do {
    rx = MidiUSB.read();
    if (rx.header != 0) {
      switch (rx.header) {
        case 0:
          break;
          
        case 0xB: // control change
          //rx.byte1 & 0xF,  //channel
          //rx.byte2,        //control
          //rx.byte3         //value
          goalPosition = rx.byte3;
          break;
      }
    }
  } while (rx.header != 0);

  // just act on most recent goal position.
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


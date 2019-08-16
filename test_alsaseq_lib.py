# Script for Running the RNN Box system EMPI v2.
import argparse
# Grove
from grove.i2c import Bus
from grove.adc import ADC
import RPi.GPIO as GPIO
import grove_display
from numpy import interp
# ALSA MIDI
import alsaseq
import alsamidi
# http://pp.com.mx/python/alsaseq/project.html
# Setup for ALSA MIDI
alsaseq.client('EMPIMIDI', 1, 1, False)
# Setup for GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


parser = argparse.ArgumentParser(description='Interface for EMPI 2.0 using Grove shield and GPIO connection.')
parser.add_argument('-m', '--mirror', dest='mirror', action="store_true", help="Mirror physical input on physical output for testing.")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose, print input and output for testing.')
parser.add_argument("--screen", dest="screen", default=False, action="store_true", help="Use OLED display for showing data.")
parser.add_argument("--servo", dest="servo", default=False, action="store_true", help="Use the servomotor for embodied output")
args = parser.parse_args()

# Functions for sending and receving from levers.

# Global vars for Grove board
POTENTIOMETER_CHANNEL = 0
SERVO_CHANNEL = 5
MIN_POT_CHANGE = 5
MIN_SERVO_CHANGE = 2
POT_MIN = 140  # 0
POT_MAX = 850  # 999
last_potentiometer_value = -100
last_servo_value = -100
last_rnn_value = 0


class GroveServo:
    INIT_DUTY_MS = 1.5  # in ms
    SERVO_PWM_FREQUENCY = 50
    MAX_DUTY_CYCLE_MS = 2.2
    MIN_DUTY_CYCLE_MS = 0.8
    MS_TO_DC_SCALE = 100 * SERVO_PWM_FREQUENCY / 1000

    def __init__(self, channel):
        GPIO.setup(channel, GPIO.OUT)
        self.pwm = GPIO.PWM(channel, GroveServo.SERVO_PWM_FREQUENCY)
        self.pwm.start(GroveServo.INIT_DUTY_MS * GroveServo.MS_TO_DC_SCALE)

    def __del__(self):
        self.pwm.stop()

    def setAngle(self, angle):
        duty_cycle_ms = interp(angle, [0, 180],
                               [GroveServo.MIN_DUTY_CYCLE_MS,
                                GroveServo.MAX_DUTY_CYCLE_MS])
        self.pwm.ChangeDutyCycle(duty_cycle_ms * GroveServo.MS_TO_DC_SCALE)


def command_servo(input):
    """Send a command to the servo. Input is between 0, 1"""
    global last_servo_value
    val = interp(input, [0, 127], [0, 180])
    # Only write significant changes to servo.
    if (abs(val - last_servo_value) > MIN_SERVO_CHANGE):
        last_servo_value = val
        grove_servo.setAngle(val)


def read_lever():
    """Read a single byte from the lever and return as float in [0, 1]."""
    global last_potentiometer_value
    inp_int = grove_adc.read(POTENTIOMETER_CHANNEL)  # read from pot
    inp_int = min(max(inp_int, POT_MIN), POT_MAX)  # limit value within a range
    if (abs(inp_int - last_potentiometer_value) > MIN_POT_CHANGE):
        last_potentiometer_value = inp_int
        return interp(inp_int, [POT_MIN, POT_MAX], [0, 1])
    else:
        return None

# Run Loop Function:

# while 1:
# 	if alsaseq.inputpending():
# 		ev = alsaseq.input()
# 		alsaseq.output(ev)
# alsaseq.connectfrom(1, 128, 0)
# alsaseq.connectto(0, 128, 0)


last_received_midi = 64
SND_SEQ_EVENT_CONTROLLER = 10


def interaction_loop():
    """Interaction loop for the box, reads serial,
    makes predictions, outputs servo and sound."""
    global last_received_midi
    # Start Lever Processing
    userloc = read_lever()
    if userloc is not None:
        if args.verbose:
            print("Input:", userloc)
        # Send MIDI to synth.
        midi_loc = int(userloc * 127)
        #midi_event = alsamidi.noteevent(1, 1, midi_loc, 0, 0)
        midi_ctl_event = (10, 1, 0, 0, (0, 0), (0, 0), (0, 0), (0, 0, 0, 0, 0, midi_loc))
        #alsaseq.output(midi_event)
        alsaseq.output(midi_ctl_event)
        print("MIDIOUT:", midi_ctl_event)
        if args.mirror:
            last_received_midi = midi_loc
    # Read incoming midi.
    while(alsaseq.inputpending() > 0):
        midi_event = alsaseq.input()
        if midi_event[0] == SND_SEQ_EVENT_CONTROLLER:
            # just take the controller value
            last_received_midi = midi_event[7][5]
        # do something with it
        if args.verbose:
            print("Servo:", last_received_midi)
            print("MIDI:", midi_event)
    command_servo(last_received_midi)

# define SERVOMIN 5
# define SERVOMAX 175

#MIDI: (10, 0, 0, 253, (0, 0), (129, 1), (128, 0), (0, 0, 0, 0, 0, 48))
#Output: 64
#MIDI: (6, 0, 0, 253, (0, 0), (129, 1), (128, 0), (0, 1, 48, 0, 0))


# Setup ADC and Servo
grove_adc = ADC()
grove_servo = GroveServo(SERVO_CHANNEL)

print("starting up.")
if args.verbose:
    print("verbose mode on.")
if args.screen:
    display = grove_display.setup_display()
# Run loop
try:
    print("interface started.")
    while True:
        interaction_loop()
except KeyboardInterrupt:
    print("\nCtrl-C received... exiting.")
    if args.screen:
        display.clear()
    pass
finally:
    print("\nshutting down.")

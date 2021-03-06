# Script for Running the RNN Box system EMPI v2.
import time
import struct
import logging
import datetime
import argparse
from threading import Thread, Condition
# OSC
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
# Grove
from grove.i2c import Bus
from grove.adc import ADC
import RPi.GPIO as GPIO
import grove_display
from numpy import interp
# Setup for GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# Details for OSC output
INTERFACE_MESSAGE_ADDRESS = "/interface"
PREDICTION_MESSAGE_ADDRESS = "/prediction"

# Input and output to serial are bytes (0-255)
# Output to Pd is a float (0-1)
parser = argparse.ArgumentParser(description='Interface for EMPI 2.0 using Grove shield and GPIO connection.')
parser.add_argument('-m', '--mirror', dest='user_to_servo', action="store_true", help="Mirror physical input on physical output for testing.")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose, print input and output for testing.')
# OSC addresses
parser.add_argument("--predictorip", default="localhost", help="The address of the IMPS prediction system.")
parser.add_argument("--predictorport", type=int, default=5001, help="The port the IMPS server is listening on.")
parser.add_argument("--synthip", default="127.0.0.1", help="The address of the synth.")
parser.add_argument("--synthport", type=int, default=3000, help="The port the synth.")
parser.add_argument("--serverip", dest='serverip', default="localhost", help="The address of this server.")
parser.add_argument("--serverport", dest='serverport', type=int, default=5000, help="The port this interface should listen on.")
parser.add_argument("--screen", dest="screen", default=False, action="store_true", help="Use OLED display for showing data.")
parser.add_argument("--servo", dest="servo", default=False, action="store_true", help="Use the servomotor for embodied output")
args = parser.parse_args()


def handle_prediction_message(address: str, *osc_arguments) -> None:
    """Handler for OSC messages from the interface"""
    if args.verbose:
        print("Prediction:", time.time(), ','.join(map(str, osc_arguments)))
    pred_loc = osc_arguments[0]
    osc_synth.send_message(PREDICTION_MESSAGE_ADDRESS, pred_loc)
    if args.servo:
        command_servo(pred_loc)
    if args.screen:
        display.set_cursor(0, 0)
        display.puts('EMPI.           ')
        display.set_cursor(1, 0)
        display.puts("RNN: {:11.4f}".format(str(osc_arguments[0])))


def interaction_loop():
    """Interaction loop for the box, reads serial,
    makes predictions, outputs servo and sound."""
    global last_user_touch
    global last_user_interaction
    global last_rnn_touch
    # Start Lever Processing
    userloc = read_lever()
    if userloc is not None:
        if args.verbose:
            print("Input:", userloc)
        # Send sound to predictor.
        osc_predictor.send_message(INTERFACE_MESSAGE_ADDRESS, userloc)
        # Send sound to synth
        osc_synth.send_message(INTERFACE_MESSAGE_ADDRESS, userloc)
        if args.user_to_servo:
            print("Input -> Servo:", userloc)
            command_servo(userloc)


# Functions for sending and receving from levers.

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
    val = interp(input, [0, 1], [0, 180])
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


# Setup inputs and outputs on Grove board.
POTENTIOMETER_CHANNEL = 0
SERVO_CHANNEL = 5
MIN_POT_CHANGE = 5
MIN_SERVO_CHANGE = 2
POT_MIN = 140  # 0
POT_MAX = 850  # 999
last_potentiometer_value = -100
last_servo_value = -100
last_rnn_value = 0

# define SERVOMIN 5
# define SERVOMAX 175

## Setup ADC
grove_adc = ADC()
## Setup Servo
grove_servo = GroveServo(SERVO_CHANNEL)


# Set up OSC client and server
osc_predictor = udp_client.SimpleUDPClient(args.predictorip, args.predictorport)
osc_synth = udp_client.SimpleUDPClient(args.synthip, args.synthport)
disp = dispatcher.Dispatcher()
disp.map(PREDICTION_MESSAGE_ADDRESS, handle_prediction_message)
server = osc_server.ThreadingOSCUDPServer((args.serverip, args.serverport), disp)
server_thread = Thread(target=server.serve_forever, name="server_thread", daemon=True)
thread_running = False


print("starting up.")
if args.verbose:
    print("Verbose mode on.")
if args.screen:
    display = grove_display.setup_display()
    display.set_cursor(0, 0)
    display.puts('EMPI Ready.')
try:
    thread_running = True
    server_thread.start()
    print("Interface server started.")
    print("Serving on {}".format(server.server_address))
    while True:
        interaction_loop()
except KeyboardInterrupt:
    print("\nCtrl-C received... exiting.")
    thread_running = False
    if args.screen:
        display.clear()
    pass
finally:
    print("\nDone, shutting down.")

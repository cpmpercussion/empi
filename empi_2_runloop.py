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
import RPi.GPIO as IO
from numpy import interp

# Details for OSC output
INTERFACE_MESSAGE_ADDRESS = "/interface"
PREDICTION_MESSAGE_ADDRESS = "/prediction"

# Input and output to serial are bytes (0-255)
# Output to Pd is a float (0-1)
parser = argparse.ArgumentParser(description='Interface for EMPI 1.0 using Arduino and Serial Connection.')
parser.add_argument('-m', '--mirror', dest='user_to_servo', action="store_true", help="Mirror physical input on physical output for testing.")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Verbose, print input and output for testing.")
# OSC addresses
parser.add_argument("--predictorip", default="localhost", help="The address of the IMPS prediction system.")
parser.add_argument("--predictorport", type=int, default=5001, help="The port the IMPS server is listening on.")
parser.add_argument("--synthip", default="localhost", help="The address of the synth.")
parser.add_argument("--synthport", type=int, default=3000, help="The port the synth.")
parser.add_argument("--serverip", default="localhost", help="The address of this server.")
parser.add_argument("--serverport", type=int, default=5000, help="The port this interface should listen on.")
args = parser.parse_args()


# Functions for OSC Connection.

def handle_prediction_message(address: str, *osc_arguments) -> None:
    """Handler for OSC messages from the interface"""
    if args.verbose:
        print("Prediction:", time.time(), ','.join(map(str, osc_arguments)))
    pred_loc = osc_arguments[0]
    osc_synth.send_message(PREDICTION_MESSAGE_ADDRESS, pred_loc)
    command_servo(pred_loc)


# Interaction Loop


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
    # # Send any waiting messages to the servo.
    # while not writing_queue.empty():
    #     servo_pos = writing_queue.get()
    #     command_servo(servo_pos)

# receive an output
# to_play_back = 0
# writing_queue.put_nowait(to_play_back)


# Functions for sending and receving from levers.


class GroveServo:
    MIN_DEGREE = 0
    MAX_DEGREE = 180
    INIT_DUTY = 2.5

    def __init__(self, channel):
        IO.setup(channel, IO.OUT)
        self.pwm = IO.PWM(channel, 50)
        self.pwm.start(GroveServo.INIT_DUTY)

    def __del__(self):
        self.pwm.stop()

    def setAngle(self, angle):
        # Map angle from range 0 ~ 180 to range 25 ~ 125
        angle = max(min(angle, GroveServo.MAX_DEGREE), GroveServo.MIN_DEGREE)
        tmp = interp(angle, [0, 180], [25, 125])
        self.pwm.ChangeDutyCycle(round(tmp/10.0, 1))


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
    if (abs(inp_int - last_potentiometer_value) > MIN_POT_CHANGE):
        last_potentiometer_value = inp_int
        return interp(inp_int, [0, 999], [0, 1])
    else:
        return None


# Setup inputs and outputs on Grove board.
POTENTIOMETER_CHANNEL = 0
SERVO_CHANNEL = 5
MIN_POT_CHANGE = 10
MIN_SERVO_CHANGE = 5
last_potentiometer_value = -100
last_servo_value = -100
last_rnn_value = 0

grove_adc = ADC()
grove_servo = GroveServo(SERVO_CHANNEL)


# Set up OSC client and server
osc_predictor = udp_client.SimpleUDPClient(args.predictorip, args.predictorport)
osc_synth = udp_client.SimpleUDPClient(args.synthip, args.synthport)
disp = dispatcher.Dispatcher()
disp.map(PREDICTION_MESSAGE_ADDRESS, handle_prediction_message)
server = osc_server.ThreadingOSCUDPServer((args.serverip, args.serverport), disp)
thread_running = False


print("starting up.")
if args.verbose:
    print("Verbose mode on.")
thread_running = True
try:
    while True:
        interaction_loop()
except KeyboardInterrupt:
    print("\nCtrl-C received... exiting.")
    thread_running = False
    pass
finally:
    print("\nDone, shutting down.")

# Script for Running the RNN Box system
import serial
from serial.tools.list_ports import comports
import time
import struct
import logging
import datetime
import argparse
from threading import Thread, Condition
import numpy as np
import queue
# OSC
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

# Details for OSC output
INTERFACE_MESSAGE_ADDRESS = "/interface"
PREDICTION_MESSAGE_ADDRESS = "/prediction"

# Input and output to serial are bytes (0-255)
# Output to Pd is a float (0-1)
parser = argparse.ArgumentParser(description='Interface for EMPI 1.0 using Arduino and Serial Connection.')
parser.add_argument('-m', '--mirror', dest='user_to_servo', action="store_true", help="Mirror physical input on physical output for testing.")
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
    # Interaction loop for the box, reads serial, makes predictions, outputs servo and sound.
    global last_user_touch
    global last_user_interaction
    global last_rnn_touch
    # Start Lever Processing
    userloc = None
    while ser.in_waiting > 0:
        userloc = read_lever()
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


def command_servo(input):
    """Send a command to the servo. Input is between 0, 1"""
    ser.write(struct.pack('B', int(input * 255)))


def read_lever():
    """Read a single byte from the lever and return as float in [0, 1]."""
    inp_int = ord(ser.read(1))
    inp_int = min(max(inp_int, 0), 255)
    inp_float = inp_int / 255.0
    return inp_float


def detect_arduino_tty():
    """ Attempts to detect a Myo Bluetooth adapter among the system's serial ports. """
    for p in comports():
        if p[1] == 'SparkFun Pro Micro':
            return p[0]
    return None

# Setup serial for input and output via a USB-connected microcontroller.
try:
    tty = detect_arduino_tty()
    print("Connecting to", tty)
    ser = serial.Serial(tty, 115200, timeout=None, write_timeout=None)
except serial.SerialException:
    print("Serial Port busy or not available.")

# Set up OSC client and server
osc_predictor = udp_client.SimpleUDPClient(args.predictorip, args.predictorport)
osc_synth = udp_client.SimpleUDPClient(args.synthip, args.synthport)
disp = dispatcher.Dispatcher()
disp.map(PREDICTION_MESSAGE_ADDRESS, handle_prediction_message)
server = osc_server.ThreadingOSCUDPServer((args.serverip, args.serverport), disp)
thread_running = False


print("starting up.")
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

# Script for Running the RNN Box system EMPI v2.
import time
import argparse
import numpy as np
from threading import Thread
# OSC
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
# Details for OSC output
INTERFACE_MESSAGE_ADDRESS = "/interface"
PREDICTION_MESSAGE_ADDRESS = "/prediction"

# Input and output to serial are bytes (0-255)
# Output to Pd is a float (0-1)
parser = argparse.ArgumentParser(description='Boilerplate EMPI interface')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Verbose, print input and output for testing.')
# OSC addresses
parser.add_argument("--predictorip", default="localhost", help="The address of the IMPS prediction system.")
parser.add_argument("--predictorport", type=int, default=5001, help="The port the IMPS server is listening on.")
parser.add_argument("--synthip", default="localhost", help="The address of the synth.")
parser.add_argument("--synthport", type=int, default=3000, help="The port the synth.")
parser.add_argument("--serverip", default="localhost", help="The address of this server.")
parser.add_argument("--serverport", type=int, default=5000, help="The port this interface should listen on.")
args = parser.parse_args()


def handle_prediction_message(address: str, *osc_arguments) -> None:
    """Handler for OSC messages from the interface"""
    if args.verbose:
        print("Prediction:", time.time(), ','.join(map(str, osc_arguments)))
    osc_synth.send_message(PREDICTION_MESSAGE_ADDRESS, osc_arguments[0])


def interaction_loop():
    """Interaction loop for the box, reads serial,
    makes predictions, outputs servo and sound."""
    userloc = np.random.rand()  # Fake data
    if userloc is not None:
        if args.verbose:
            print("Input:", userloc)
        osc_predictor.send_message(INTERFACE_MESSAGE_ADDRESS, userloc)
        osc_synth.send_message(INTERFACE_MESSAGE_ADDRESS, userloc)


# Set up OSC client and server
osc_predictor = udp_client.SimpleUDPClient(args.predictorip, args.predictorport)
osc_synth = udp_client.SimpleUDPClient(args.synthip, args.synthport)
disp = dispatcher.Dispatcher()
disp.map(PREDICTION_MESSAGE_ADDRESS, handle_prediction_message)
server = osc_server.ThreadingOSCUDPServer((args.serverip, args.serverport), disp)
server_thread = Thread(target=server.serve_forever, name="server_thread", daemon=True)

print("Interface server started.")
print("Serving on {}".format(server.server_address))

thread_running = False


print("starting up.")
if args.verbose:
    print("Verbose mode on.")
try:
    thread_running = True
    server_thread.start()
    while True:
        interaction_loop()
        time.sleep(5)  # Fake time.
except KeyboardInterrupt:
    print("\nCtrl-C received... exiting.")
    thread_running = False
    pass
finally:
    print("\nDone, shutting down.")

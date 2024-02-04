import logging
import time
import datetime
import numpy as np
import queue
import serial
import argparse
from threading import Thread
ser = serial.Serial('/dev/ttyAMA0', baudrate=31250)


# Input and output to serial are bytes (0-255)
# Output to Pd is a float (0-1)
parser = argparse.ArgumentParser(description='Predictive Musical Interaction MDRNN Interface.')
parser.add_argument('-l', '--log', dest='logging', action="store_true", help='Save input and RNN data to a log file.')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", help='Verbose mode, print prediction results.')
# Performance modes
parser.add_argument('-o', '--only', dest='useronly', action="store_true", help="User control only mode, no RNN.")
parser.add_argument('-c', '--call', dest='callresponse', action="store_true", help='Call and response mode.')
parser.add_argument('-p', '--polyphony', dest='polyphony', action="store_true", help='Harmony mode.')
parser.add_argument('-b', '--battle', dest='battle', action="store_true", help='Battle royale mode.')
parser.add_argument('--callresponsethresh', type=float, default=2.0, help="Seconds to wait before switching to response")
# OSC addresses
parser.add_argument("--clientip", default="localhost", help="The address of output device.")
parser.add_argument("--clientport", type=int, default=5000, help="The port the output device is listening on.")
parser.add_argument("--serverip", default="localhost", help="The address of this server.")
parser.add_argument("--serverport", type=int, default=5001, help="The port this server should listen on.")
# MDRNN arguments.
parser.add_argument('-d', '--dimension', type=int, dest='dimension', default=2, help='The dimension of the data to model, must be >= 2.')
parser.add_argument('-s', '--modelsize', dest='modelsize', default='s', help="The model size: xs, s, m, l, xl")
parser.add_argument("--sigmatemp", type=float, default=0.01, help="The sigma temperature for sampling.")
parser.add_argument("--pitemp", type=float, default=1, help="The pi temperature for sampling.")
# Custom Model File:
parser.add_argument('--modelfile', dest="modelfile", default="", help="Location of a custom model file.")
args = parser.parse_args()
# Import Keras and tensorflow, doing this later to make CLI more responsive.
print("Importing MDRNN.")
start_import = time.time()
import empi_mdrnn
import tensorflow.compat.v1 as tf
print("Done. That took", time.time() - start_import, "seconds.")

# Choose model parameters.
if args.modelsize == 'xs':
    print("Using XS model.")
    mdrnn_units = 32
    mdrnn_mixes = 5
    mdrnn_layers = 2
elif args.modelsize == 's':
    print("Using S model.")
    mdrnn_units = 64
    mdrnn_mixes = 5
    mdrnn_layers = 2
elif args.modelsize == 'm':
    print("Using M model.")
    mdrnn_units = 128
    mdrnn_mixes = 5
    mdrnn_layers = 2
elif args.modelsize == 'l':
    print("Using L model.")
    mdrnn_units = 256
    mdrnn_mixes = 5
    mdrnn_layers = 2
elif args.modelsize == 'xl':
    print("Using XL model.")
    mdrnn_units = 512
    mdrnn_mixes = 5
    mdrnn_layers = 3

# Interaction Loop Parameters
# All set to false before setting is chosen.
user_to_rnn = False
rnn_to_rnn = False
rnn_to_sound = False

# Interactive Mapping
if args.callresponse:
    print("Entering call and response mode.")
    # set initial conditions.
    user_to_rnn = True
    rnn_to_rnn = False
    rnn_to_sound = False
elif args.polyphony:
    print("Entering polyphony mode.")
    user_to_rnn = True
    rnn_to_rnn = False
    rnn_to_sound = True
elif args.battle:
    print("Entering battle royale mode.")
    user_to_rnn = False
    rnn_to_rnn = True
    rnn_to_sound = True
elif args.useronly:
    print("Entering user only mode.")
    user_to_rnn = False
    rnn_to_rnn = False
    rnn_to_sound = False


def build_network(sess):
    """Build the MDRNN."""
    empi_mdrnn.MODEL_DIR = "./models/"
    tf.keras.backend.set_session(sess)
    with compute_graph.as_default():
        net = empi_mdrnn.PredictiveMusicMDRNN(mode=empi_mdrnn.NET_MODE_RUN,
                                              dimension=args.dimension,
                                              n_hidden_units=mdrnn_units,
                                              n_mixtures=mdrnn_mixes,
                                              layers=mdrnn_layers)
        net.pi_temp = args.pitemp
        net.sigma_temp = args.sigmatemp
    print("MDRNN Loaded:", net.model_name())
    return net


def request_rnn_prediction(input_value):
    """ Accesses a single prediction from the RNN. """
    output_value = net.generate_touch(input_value)
    return output_value


def make_prediction(sess, compute_graph):
    # Interaction loop: reads input, makes predictions, outputs results.
    # Make predictions.

    # First deal with user --> MDRNN prediction
    if user_to_rnn and not interface_input_queue.empty():
        item = interface_input_queue.get(block=True, timeout=None)
        tf.keras.backend.set_session(sess)
        with compute_graph.as_default():
            rnn_output = request_rnn_prediction(item)
        if args.verbose:
            print("User->RNN prediction:", rnn_output)
        if rnn_to_sound:
            rnn_output_buffer.put_nowait(rnn_output)
        interface_input_queue.task_done()

    # Now deal with MDRNN --> MDRNN prediction.
    if rnn_to_rnn and rnn_output_buffer.empty() and not rnn_prediction_queue.empty():
        item = rnn_prediction_queue.get(block=True, timeout=None)
        tf.keras.backend.set_session(sess)
        with compute_graph.as_default():
            rnn_output = request_rnn_prediction(item)
        if args.verbose:
            print("RNN->RNN prediction out:", rnn_output)
        rnn_output_buffer.put_nowait(rnn_output)  # put it in the playback queue.
        rnn_prediction_queue.task_done()


last_note_played = 0

def send_sound_command(command_args):
    """Send a sound command back to the interface/synth"""
    global last_note_played
    assert len(command_args)+1 == args.dimension, "Dimension not same as prediction size." # Todo more useful error.
    # TODO put in serial sending code here
    # should just send "note on" based on first argument.
    channel = 0
    ## order is (cmd/channel), pitch, vel
    ser.write(bytearray([(8 << 4) | channel, last_note_played, 0])) # stop last note
    new_note = int(ceil(command_args[0] * 127)) # calc new note
    ser.write(bytearray([(9 << 4) | channel, new_note, 127])) # play new note
    print(f'sent MIDI note: {new_note}')
    last_note_played = new_note # remember last note played


def playback_rnn_loop():
    # Plays back RNN notes from its buffer queue.
    while True:
        item = rnn_output_buffer.get(block=True, timeout=None)  # Blocks until next item is available.
        # print("processing an rnn command", time.time())
        dt = item[0]
        x_pred = np.minimum(np.maximum(item[1:], 0), 1)
        dt = max(dt, 0.001)  # stop accidental minus and zero dt.
        time.sleep(dt)  # wait until time to play the sound
        # put last played in queue for prediction.
        rnn_prediction_queue.put_nowait(np.concatenate([np.array([dt]), x_pred]))
        if rnn_to_sound:
            send_sound_command(x_pred)
            # print("RNN Played:", x_pred, "at", dt)
            logging.info("{1},rnn,{0}".format(','.join(map(str, x_pred)),
                         datetime.datetime.now().isoformat()))
        rnn_output_buffer.task_done()


def monitor_user_action():
    # Handles changing responsibility in Call-Response mode.
    global call_response_mode
    global user_to_rnn
    global rnn_to_rnn
    global rnn_to_sound
    # Check when the last user interaction was
    dt = time.time() - last_user_interaction_time
    if dt > args.callresponsethresh:
        # switch to response modes.
        user_to_rnn = False
        rnn_to_rnn = True
        rnn_to_sound = True
        if call_response_mode == 'call':
            print("switching to response.")
            call_response_mode = 'response'
            while not rnn_prediction_queue.empty():
                # Make sure there's no inputs waiting to be predicted.
                rnn_prediction_queue.get()
                rnn_prediction_queue.task_done()
            rnn_prediction_queue.put_nowait(last_user_interaction_data)  # prime the RNN queue
    else:
        # switch to call mode.
        user_to_rnn = True
        rnn_to_rnn = False
        rnn_to_sound = False
        if call_response_mode == 'response':
            print("switching to call.")
            call_response_mode = 'call'
            # Empty the RNN queues.
            while not rnn_output_buffer.empty():
                # Make sure there's no actions waiting to be synthesised.
                rnn_output_buffer.get()
                rnn_output_buffer.task_done()


# Logging
LOG_FILE = datetime.datetime.now().isoformat().replace(":", "-")[:19] + "-" + str(args.dimension) + "d" +  "-mdrnn.log"  # Log file name.
LOG_FILE = "logs/" + LOG_FILE
LOG_FORMAT = '%(message)s'

if args.logging:
    logging.basicConfig(filename=LOG_FILE,
                        level=logging.INFO,
                        format=LOG_FORMAT)
    print("Logging enabled:", LOG_FILE)
# Details for OSC output
INPUT_MESSAGE_ADDRESS = "/interface"
OUTPUT_MESSAGE_ADDRESS = "/prediction"

# Set up runtime variables.
# ## Load the Model
compute_graph = tf.Graph()
with compute_graph.as_default():
    sess = tf.Session()
net = build_network(sess)
interface_input_queue = queue.Queue()
rnn_prediction_queue = queue.Queue()
rnn_output_buffer = queue.Queue()
writing_queue = queue.Queue()
last_user_interaction_time = time.time()
last_user_interaction_data = empi_mdrnn.random_sample(out_dim=args.dimension)
rnn_prediction_queue.put_nowait(empi_mdrnn.random_sample(out_dim=args.dimension))
call_response_mode = 'call'

thread_running = True  # todo is this line needed?

# Set up run loop.
print("Preparing MDRNN.")
tf.keras.backend.set_session(sess)
with compute_graph.as_default():
    if args.modelfile != "":
        net.load_model(model_file=args.modelfile) # load custom model.
    else:
        net.load_model()  # try loading from default file location.
print("Preparting MDRNN thread.")
rnn_thread = Thread(target=playback_rnn_loop, name="rnn_player_thread", daemon=True)

try:
    rnn_thread.start()
    while True:
        make_prediction(sess, compute_graph)
        if args.callresponse:
            monitor_user_action()
except KeyboardInterrupt:
    print("\nCtrl-C received... exiting.")
    thread_running = False
    rnn_thread.join(timeout=0.1)
    pass
finally:
    print("\nDone, shutting down.")

#!/usr/bin/python
import random
import numpy as np
import os
import argparse
import time
import datetime

# Hack to get openMP working annoyingly.
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

parser = argparse.ArgumentParser(description='Script to train a predictive music interaction model for EMPI.')
parser.add_argument('-p', '--human', dest='human', action="store_true", help='Train the human model.')
parser.add_argument('-s', '--synth', dest='synth', action="store_true", help='Train the synth model.')
parser.add_argument('-n', '--noise', dest='noise', action="store_true", help='Train the noise model.')
parser.add_argument('-m', '--modelsize', dest='modelsize', default='xs', help="The model size: xs, s, m, l, xl")
parser.add_argument('-e', "--noearlystopping", dest='earlystopping', action="store_false", help="Use early stopping")
args = parser.parse_args()

print("Script to train a predictive music interaction model for EMPI.")

EARLY_STOPPING = args.earlystopping # default is true
PATIENCE = 10
MODEL_SIZE = args.modelsize # xs
DIMENSION = 2
HUMAN_DATA_LOCATION = 'datasets/empi-human-dataset.npz'
SYNTH_DATA_LOCATION = 'datasets/empi-synthetic-dataset.npz'
NOISE_DATA_LOCATION = 'datasets/empi-noise-dataset.npz'


if (args.human):
    print("Training human model.")
    DATA_LOCATION = HUMAN_DATA_LOCATION
    MODEL_SUFFIX = "human"

if (args.synth):
    print("Training synth model.")
    DATA_LOCATION = SYNTH_DATA_LOCATION
    MODEL_SUFFIX = "synth"

if (args.noise):
    print("Training noise model.")
    DATA_LOCATION = NOISE_DATA_LOCATION
    MODEL_SUFFIX = "noise"


# Import Keras
import empi_mdrnn
import keras
import keras.backend as K
import tensorflow as tf
# Set up environment.
# Only for GPU use:
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
K.set_session(sess)

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

print("Model size:", MODEL_SIZE)
print("Units:", mdrnn_units)
print("Layers:", mdrnn_layers)
print("Mixtures:", mdrnn_mixes)
print("EarlyStopping:", EARLY_STOPPING)

# Model Hyperparameters
SEQ_LEN = 50
SEQ_STEP = 1
TIME_DIST = True

# Training Hyperparameters:
BATCH_SIZE = 64
EPOCHS = 100
VAL_SPLIT = 0.10

# Set random seed for reproducibility
SEED = 2345
random.seed(SEED)
np.random.seed(SEED)

with np.load(DATA_LOCATION, allow_pickle=True) as loaded:
    perfs = loaded['perfs']

print("Loaded perfs:", len(perfs))
print("Num touches:", np.sum([len(l) for l in perfs]))
corpus = perfs  # might need to do some processing here...processing
# Restrict corpus to sequences longer than the corpus.
corpus = [l for l in corpus if len(l) > SEQ_LEN+1]
print("Corpus Examples:", len(corpus))
# Prepare training data as X and Y.
slices = []
for seq in corpus:
    slices += empi_mdrnn.slice_sequence_examples(seq,
                                                 SEQ_LEN+1,
                                                 step_size=SEQ_STEP)
X, y = empi_mdrnn.seq_to_overlapping_format(slices)
X = np.array(X) * empi_mdrnn.SCALE_FACTOR
y = np.array(y) * empi_mdrnn.SCALE_FACTOR

print("Number of training examples:")
print("X:", X.shape)
print("y:", y.shape)

# Setup Training Model
model = empi_mdrnn.build_model(seq_len=SEQ_LEN,
                               hidden_units=mdrnn_units,
                               num_mixtures=mdrnn_mixes,
                               layers=mdrnn_layers,
                               out_dim=DIMENSION,
                               time_dist=TIME_DIST,
                               inference=False,
                               compile_model=True,
                               print_summary=True)

model_dir = "models/"
model_name = "musicMDRNN" + "-dim" + str(DIMENSION) + "-layers" + str(mdrnn_layers) + "-units" + str(mdrnn_units) + "-mixtures" + str(mdrnn_mixes) + "-scale" + str(empi_mdrnn.SCALE_FACTOR) + "-" + MODEL_SUFFIX
date_string = datetime.datetime.today().strftime('%Y%m%d-%H_%M_%S')

filepath = model_dir + model_name + "-E{epoch:02d}-VL{val_loss:.2f}.hdf5"
checkpoint = keras.callbacks.ModelCheckpoint(filepath,
                                             monitor='val_loss',
                                             verbose=1,
                                             save_best_only=True,
                                             mode='min')
terminateOnNaN = keras.callbacks.TerminateOnNaN()
early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=PATIENCE)
tboard = keras.callbacks.TensorBoard(log_dir='./logs/' + date_string + model_name,
                                     histogram_freq=2,
                                     batch_size=32,
                                     write_graph=True,
                                     update_freq='epoch')
callbacks = [checkpoint, terminateOnNaN, tboard]
# Early stopping
if EARLY_STOPPING:
    callbacks.append(early_stopping)
# Train
history = model.fit(X, y, batch_size=BATCH_SIZE,
                    epochs=EPOCHS,
                    validation_split=VAL_SPLIT,
                    callbacks=callbacks)

# Save final Model
model.save_weights(model_dir + model_name + ".h5")

print("Done, bye.")

#!/bin/bash
servo=1 # default on
# 0 = off, 1 = on, 2 = disconnected
model=2 # default off
# 0 = noise, 1 = synth, 2 = human
# Process arguments
for arg in "$@"
do
    if [ "$arg" == "--noise" ]
    then
        echo "Noise Model"
        model=0
    elif [ "$arg" == "--synth" ]
    then
        echo "Synth Model"
        model=1
    elif [ "$arg" == "--human" ]
    then
        echo "Human Model"
        model=2
    elif [ "$arg" == "--noservo" ]
    then
        echo "No Servo Mode"
        servo=0
    elif [ "$arg" == "--servo" ]
    then
        echo "Servo Mode"
        servo=1
    elif [ "$arg" == "--disco" ]
    then
        echo "Disconnected Servo Mode"
        servo=2
    fi
done

# echo $model
# echo $servo

# Start opening software.
cd /home/pi/empi

# Ignores servo mode for now, doesn't need empi_alsa_midi_interface script.

# # start the alsa midi interface.
# if [ $servo -eq 0 ]
# then
#     ## no servo
#     python3 empi_alsa_midi_interface.py --screen &
#     echo "No Servo Mode"
# elif [ $servo -eq 1 ]
# then
#     ## connected servo
#     python3 empi_alsa_midi_interface.py --servo --screen &
#     echo "Servo Mode"
# elif [ $servo -eq 2 ]
# then
#     ## disconnect servo
#     python3 empi_alsa_midi_interface.py --screen & 
# else
#     echo "No servo mode chosen, shutting down."
# fi

# Start Pd
pd -nogui -alsamidi -audiooutdev 1 -audiobuf 50 -mididev 128 -noadc -nrt -verbose -open synth/lever_synthesis_midi.pd &
sleep 4
aconnect SparkFun\ Pro\ Micro:1 Pure\ Data:0
aconnect Pure\ Data:1 SparkFun\ Pro\ Micro:0
# wait a bit
sleep 3

# Start prediction server
if [ $model -eq 0 ]
then
    echo "Noise Model"
    python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-noise.h5" --modelsize xs --call --log --verbose
elif [ $model -eq 1 ]
then
    echo "Synth Model"
    python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-synth.h5" --modelsize xs --call --log --verbose
elif [ $model -eq 2 ]
then
    echo "Human Model"
    python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-human.h5" --modelsize xs --call --log --verbose
else
    echo "No model chosen, shutting down."
fi

# Start interface
#python3 empi_2_runloop.py --screen
# After the RNN box controller exits, stop Pd
pkill -u pi pd
pkill -u pi python3

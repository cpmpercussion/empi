#!/bin/bash
servo = 0
# 0 = off, 1 = on, 2 = disconnected
model = 0
# 0 = noise, 1 = synth, 2 = human
# Process arguments
for arg in "$@"
do
    if [ "$arg" == "--noise" ]
    then
        echo "Noise Model"
        model = 0
    elif [ "$arg" == "--synth" ]
    then
        echo "Synth Model"
        model = 1
    elif [ "$arg" == "--human" ]
    then
        echo "Human Model"
        model = 2
    elif [ "$arg" == "--noservo" ]
    then
        echo "No servo mode"
        model = 0
    elif [ "$arg" == "--servo" ]
    then
        echo "Servo mode"
        model = 1
    elif [ "$arg" == "--disco" ]
    then
        echo "Disconnected servo mode"
        model = 2
    fi
done

# Start opening software.
cd /home/pi/empi

# start the alsa midi interface.
if [ $servo -eq 0 ]
then
    ## no servo
    python3 empi_alsa_midi_interface.py &
elif [ $servo -eq 1 ]
then
    ## connected servo
    python3 empi_alsa_midi_interface.py --servo &
elif [ $servo -eq 2 ]
then
    ## disconnect servo
    python3 empi_alsa_midi_interface.py & 
else
    echo "No servo mode chosen, shutting down."
fi

# Start Pd
./start_pd.sh
# wait a bit
sleep 3

# Start prediction server
if [ $model -eq 0 ]
then 
    python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-noise.h5" --modelsize xs --call --log --verbose
elif [ $model -eq 1 ]
then
    python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-synth.h5" --modelsize xs --call --log --verbose
elif [ $model -eq 2 ]
then
    python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-human.h5" --modelsize xs --call --log --verbose
else
    echo "No model chosen, shutting down."
fi

# Start interface
#python3 empi_2_runloop.py --screen
# After the RNN box controller exits, stop Pd
pkill -u pi pd
pkill -u pi python3

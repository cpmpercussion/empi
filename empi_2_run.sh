#!/bin/bash
cd /home/pi/empi
# start the alsa midi interface.
python3 empi_alsa_midi_interface.py &
# Start Pd
./start_pd.sh
# wait a bit
sleep 3
# Start prediction server
#python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-human.h5" --modelsize xs --call --log --verbose &
python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-synth.h5" --modelsize xs --call --log --verbose &

# Start interface
#python3 empi_2_runloop.py --screen
# After the RNN box controller exits, stop Pd
pkill -u pi pd
pkill -u pi python3

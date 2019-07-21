#!/bin/bash
cd /home/pi/empi
# Start Pd
./start_pd.sh
# Start prediction server
python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-E49-VL-2.60.hdf5" --modelsize xs --call --log --verbose &
# Start interface
python3 empi_2_runloop.py --screen
# After the RNN box controller exits, stop Pd
pkill -u pi pd
pkill -u pi python3

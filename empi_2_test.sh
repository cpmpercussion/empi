#!/bin/bash
cd /home/pi/empi
# Start Pd
./start_pd.sh
# Start the interface controller only.
python3 empi_2_runloop.py -vm
# After the RNN box controller exits, stop Pd
pkill -u pi pd

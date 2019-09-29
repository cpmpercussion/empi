#!/bin/bash
# human
python3.7 train_empi_mdn.py -p --noearlystopping -m=xs
python3.7 train_empi_mdn.py -p --noearlystopping -m=s
python3.7 train_empi_mdn.py -p --noearlystopping -m=m
python3.7 train_empi_mdn.py -p --noearlystopping -m=l
# synth
#python3.7 train_empi_mdn.py -s --noearlystopping -m=xs
#python3.7 train_empi_mdn.py -s --noearlystopping -m=s
#python3.7 train_empi_mdn.py -s --noearlystopping -m=m
#python3.7 train_empi_mdn.py -s --noearlystopping -m=l
# noise
#python3.7 train_empi_mdn.py -n --noearlystopping -m=xs
#python3.7 train_empi_mdn.py -n --noearlystopping -m=s
#python3.7 train_empi_mdn.py -n --noearlystopping -m=m
#python3.7 train_empi_mdn.py -n --noearlystopping -m=l
# done.

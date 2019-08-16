#!/bin/bash
# starts Pd synthesis process
pd -nogui -alsamidi -audiooutdev 1 -midiindev 20 -midioutdev 20 -noadc -open synth/lever_synthesis_midi.pd &
# Driver: sudo modprobe snd_seq_midi
# view midi devices: aseqdump -l
# view connections: aconnect -l
# https://github.com/arduino-libraries/MIDIUSB
# https://github.com/BlokasLabs/USBMIDI
# pkill -u pi pd
pd -nogui -alsamidi -audiooutdev 1 -mididev 128 -noadc -open synth/lever_synthesis_midi.pd &
aconnect 20 128
# https://alsa.opensrc.org/AlsaMidiOverview

# python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-human.h5" --modelsize xs --call --log --verbose

# restart alsa output
# alsa xrun recovery apparently failed
# pd: pcm.c:1168: snd_pcm_prepare: Assertion `pcm' failed.
# Pd: signal 6


# aconnect EMPIMIDI:1 Pure\ Data:0
# aconnect Pure\ Data:1 EMPIMIDI:0

#!/bin/bash
echo "running experiment condition 3"
/home/pi/empi/empi_usb_run.sh --noise --servo
# Experiment Conditions
# 1. human / servo
# 2. synth / servo
# 3. noise / servo
# 4. human / no-servo
# 5. synth / no-servo
# 6. noise / no-servo

# - Human, servo: `./empi_usb_run.sh --human --servo`
# - Synth, servo: `./empi_usb_run.sh --synth --servo`
# - Noise, servo: `./empi_usb_run.sh --noise --servo`
# - Human, no servo: `./empi_usb_run.sh --human --noservo`
# - Synth, no servo: `./empi_usb_run.sh --synth --noservo`
# - Noise, no servo: `./empi_usb_run.sh --noise --noservo`

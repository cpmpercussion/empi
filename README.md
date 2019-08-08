# EMPI: Embodied Musical Predictive Interface

An embedded musical instrument for studying musical prediction and embodied interaction.

<!-- <video src="https://giphy.com/gifs/KFoOINQn0moVJB8uUe/html5"></video> -->

![](https://media.giphy.com/media/KFoOINQn0moVJB8uUe/giphy.gif)

![Musical MDN Example](https://github.com/cpmpercussion/creative-mdns/raw/master/images/rnn_output.png)

In this work musical data is considered to consist a time-series of continuous valued events. We seek to model the values of the events as well as the time in between each one. That means that these networks model data of at least two dimensions (event value and time).

Multiple implementations of a mixture density recurrent neural network are included for comparison.

## MDN Interaction Interface

Part of this work is concerned with using these networks in a Raspberry Pi-based musical interface.

<!-- ![Musical Interface](https://github.com/cpmpercussion/creative-mdns/raw/master/images/rnn-interface.jpg) -->

### Installing on Raspberry Pi

Some of these files are intended to be used on a Raspberry Pi. Installing Tensorflow on RPi is tricky given that there is no official build, however, various unofficial builds can be found.

For our work, we use `DeftWork`'s build of Tensorflow 1.3.0 as follows:

    wget https://github.com/DeftWork/rpi-tensorflow/raw/master/tensorflow-1.3.0-cp34-cp34m-linux_armv7l.whl
    sudo pip3 install tensorflow-1.3.0-cp34-cp34m-linux_armv7l.whl

There's build instructions for Raspberry courtesy of [samjabrahams](https://github.com/samjabrahams/tensorflow-on-raspberry-pi) and more info on a possible Docker solution from [DeftWork](https://github.com/DeftWork/rpi-tensorflow). Thanks internets!

In addition to tensorflow, you also need `pandas`, `numpy` and `pySerial`. Then the interface controller can be run like so:

    python3 musical_mdn_interface_controller.py

## Assembly

![](https://media.giphy.com/media/KeKzvZvpjpWcKgXFzR/giphy.gif)

The EMPI consists of a Raspberry Pi, audio amplifier and speaker, input lever, and output lever, in a 3D-printed enclosure. The assembly materials and plans are below.

### Raspberry Pi

- Raspberry Pi 3B+
- Seeed Studios Grove Base Hat

### Training

1. download or generate some human data, then run `train_human_empi_mdn.py` to train the human model.
2. use `train_synthetic_mdn_data` notebook to generate and train synthetic data.

### SSH Access

You'll need ssh access to install EMPI: `ssh pi@rp1802.local`.

### Install the service

EMPI's startup script uses a systemd service to start automatically ([link](https://www.raspberrypi.org/documentation/linux/usage/systemd.md)).

To override this for studies etc, run:

	sudo systemctl stop empistartup.service

The service file simply runs the script: `empi_2_run.sh`






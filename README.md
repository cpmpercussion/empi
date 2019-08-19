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

### Assembly

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

### Raspbian Packages

	sudo apt-get install -y python3-numpy python3-pandas puredata

### Python Packages

- [Tensorflow 1.14.0](https://github.com/PINTO0309/Tensorflow-bin)
- [Tensorflow probability 0.7.0]()

	wget https://github.com/PINTO0309/Tensorflow-bin/raw/master/tensorflow-1.14.0-cp37-cp37m-linux_armv7l.whl
	sudo pip3 install tensorflow-1.14.0-cp37-cp37m-linux_armv7l.whl

### Install the service

EMPI's startup script uses a systemd service to start automatically ([link](https://www.raspberrypi.org/documentation/linux/usage/systemd.md)).

To override this for studies etc, run:

	sudo systemctl stop empistartup.service

The service file simply runs the script: `empi_2_run.sh`

#### Start just Pd:

	./start_pd.sh 

	pd -nogui synth/lever_synthesis.pd &

#### Start just the prediction server:

	python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-human.h5" --modelsize xs --call --log --verbose &


#### Stop Pd and Python:

	pkill -u pi pd
	pkill -u pi python3
	pkill -u pi python3

#### Start prediction server on local system:

	python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-human.h5" --modelsize xs --call --log --verbose --clientip="rp1802.local"

	python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-synth.h5" --modelsize xs --call --log --verbose --clientip="rp1802.local"

	python3 predictive_music_model.py -d=2 --modelfile="models/musicMDRNN-dim2-layers2-units32-mixtures5-scale10-noise.h5" --modelsize xs --call --log --verbose --clientip="rp1802.local" --serverip="voyager.local"

#### Start RNN run loop to send/receive from local system

	python3 empi_2_runloop.py --synthip="127.0.0.1" --serverip="rp1802.local" -v

	python3 empi_2_runloop.py --synthip="127.0.0.1" --serverip="rp1802.local" --predictorip="voyager.local" -v

### Study Procedure:

1. Connect to EMPI over ssh: `ssh pi@rp1802.local`
2. Cancel existing EMPI process with: `sudo systemctl stop empistartup.service`
3. Go to EMPI directory: `cd empi`
4. Choose commmand for required option from the list below.
5. It takes 25s to load the system on the RPi 3B+

- Human, no servo: `./empi_2_run.sh --human --noservo`
- Synth, no servo: `./empi_2_run.sh --synth --noservo`
- Noise, no servo: `./empi_2_run.sh --noise --noservo`
- Human, servo: `./empi_2_run.sh --human --servo`
- Synth, servo: `./empi_2_run.sh --synth --servo`
- Noise, servo: `./empi_2_run.sh --noise --servo`

Finally, shutdown before turning off: `sudo shutdown -h now`

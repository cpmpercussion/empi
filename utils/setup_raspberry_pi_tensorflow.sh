#!/bin/bash
sudo apt-get update
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y python3-numpy
sudo apt-get install -y python3-pandas
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools

# Python Libraries 

pip3 install tensorflow
pip3 install keras
pip3 install python-osc

# May be able to update this now with newer versions of tensorflow available.
pip3 install --no-cache-dir -I tensorflow-probability=0.4.0

# Install Keras MDN Layer
pip3 install git+git://github.com/cpmpercussion/keras-mdn-layer.git#egg=keras-mdn-layer

# Install Grove Library
curl -sL https://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s -


# Adafruit small OLED driver:
# sudo python -m pip install --upgrade pip setuptools wheel
# git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
# cd Adafruit_Python_SSD1306
# sudo python setup.py install
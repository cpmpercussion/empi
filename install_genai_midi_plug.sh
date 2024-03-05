#!/bin/sh
# Setup Tensorflow
sudo apt update && sudo apt -y full-upgrade
sudo apt update && sudo apt upgrade -y && \
sudo apt install -y \
    libhdf5-dev \
    unzip \
    pkg-config \
    python3-pip \
    cmake \
    make \
    git \
    python-is-python3 \
    wget \
    patchelf && \
pip install -U pip --break-system-packages && \
pip install numpy==1.26.2 --break-system-packages && \
pip install keras_applications==1.0.8 --no-deps --break-system-packages && \
pip install keras_preprocessing==1.1.2 --no-deps --break-system-packages && \
pip install h5py==3.10.0 --break-system-packages && \
pip install pybind11==2.9.2 --break-system-packages && \
pip install packaging --break-system-packages && \
pip install protobuf==3.20.3 --break-system-packages && \
pip install six wheel mock gdown --break-system-packages
pip uninstall tensorflow
TFVER=2.15.0.post1
PYVER=311
ARCH=`python -c 'import platform; print(platform.machine())'`
echo CPU ARCH: ${ARCH}

pip install \
--no-cache-dir \
--break-system-packages \
https://github.com/PINTO0309/Tensorflow-bin/releases/download/v${TFVER}/tensorflow-${TFVER}-cp${PYVER}-none-linux_${ARCH}.whl

# Setup other python packages.
pip install -U tensorflow-probability==0.23.0 --break-system-packages && \
pip install -U python-osc --break-system-packages && \
pip install -U keras-mdn-layer --break-system-packages && \
pip install -U pyserial --break-system-packages && \
pip install -U websockets --break-system-packages

# Setup Ethernet gadget according to: https://forums.raspberrypi.com/viewtopic.php?p=2184846
cat >/etc/network/interfaces.d/g_ether <<'EOF'
auto usb0
allow-hotplug usb0
iface usb0 inet static
        address 169.254.1.1
        netmask 255.255.0.0

auto usb0.1
allow-hotplug usb0.1
iface usb0.1 inet dhcp

EOF

## Ethernet gadget setup:

# probably add to /boot/config.txt 
# dtoverlay=dwc2
sudo echo -e "\ndtoverlay=dwc2" >> /boot/firmware/config.txt

## TODO
# add to end of  /boot/firmware/cmdline.txt
# modules-load=dwc2,g_ether

## Enable UART0
# https://www.raspberrypi.com/documentation/computers/configuration.html#uarts-and-device-tree
# Add this to /boot/firmware/config.txt: dtoverlay=disable-bt
sudo echo -e "\ndtoverlay=disable-bt" >> /boot/firmware/config.txt
sudo systemctl disable hciuart

# Reboot!
# sudo reboot

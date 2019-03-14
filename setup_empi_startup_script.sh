#!/bin/bash
cd /home/pi/empi
sudo cp /home/pi/empi/empistartup.service /etc/systemd/system/empistartup.service
sudo chmod 644 /etc/systemd/system/empistartup.service
#sudo systemctl start empistartup.service
# sudo systemctl stop empistartup.service
sudo systemctl enable empistartup.service

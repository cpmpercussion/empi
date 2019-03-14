#!/bin/bash
cd /home/pi/empi
sudo cp /home/pi/empi/empistartup /etc/init.d/
sudo chmod 755 /etc/init.d/empistartup
sudo update-rc.d empistartup defaults

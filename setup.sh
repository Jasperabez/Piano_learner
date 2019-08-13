#!/bin/bash
sudo pip3 install mido rpi_ws281x adafruit-circuitpython-neopixel
echo "[Unit]
Description=My Script Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/pi/piano_learner/pianoscript.sh

[Install]
WantedBy=multi-user.target" >> /lib/systemd/system/piano_learner.service
sudo chmod +x /home/pi/piano_learner/pianoscript.sh
sudo chmod 644 /lib/systemd/system/piano_learner.service
sudo systemctl daemon-reload
sudo systemctl enable piano_learner.service
echo "please reboot"
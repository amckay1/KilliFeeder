#!/bin/bash
# https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

# backup and edit /etc/network/interfaces
cp /etc/network/interfaces /etc/network/interfaces.backup
cp $HOME/KilliFeeder/Software/Server/setup_scripts/interfaces /etc/network/interfaces

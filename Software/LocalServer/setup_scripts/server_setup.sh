#!/bin/bash

# 0 change password to Killifish, setup internet wifi
#sudo passwd root
#sudo passwd pi
#sudo apt-get update
#sudo apt-get install git -y
#git clone https://github.com/amckay1/KilliFeeder.git

# 1 pull required software
sudo apt-get update
sudo apt-get install libpng-dev unzip wget libarchive-dev libtool m4 tmux automake squashfs-tools build-essential clang cmake gfortran -y
#sudo apt-get install mysql-server -y # need to setup table here
sudo apt-get install vim python-pip python3-pip -y
#sudo apt-get install hostapd vim dnsmasq python-pip python3-pip -y

# 2 get repo

# install Julia
wget https://julialang-s3.julialang.org/bin/linux/armv7l/1.0/julia-1.0.5-linux-armv7l.tar.gz
tar -xzf julia-1.0.5-linux-armv7l.tar.gz
rm julia-1.0.5-linux-armv7l.tar.gz
mv julia-1.0.5 $HOME
sudo ln -s $HOME/julia-1.0.5/bin/julia /usr/local/bin/julia

#git clone git://github.com/JuliaLang/julia.git
# cd julia
#git checkout release-0.6
#git fetch
#make -C deps uninstall-llvm
#make USE_BINARYBUILDER_LLVM=1 BINARYBUILDER_TRIPLET=aarch64-linux-gnu
#make install
#sudo ln -s /home/pi/julia/julia /usr/local/bin/julia
#julia Software/Server/utils/load_packages.jl


# set datetime to local
# enable SSH

# install paho
sudo pip3 install paho-mqtt
sudo apt-get install mosquitto mosquitto-clients -y




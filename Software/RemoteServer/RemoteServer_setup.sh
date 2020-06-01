#!/bin/bash

##########################################################################################
# Overview: clone repo, install Julia, set datetime to local, setup watchman as service
# setup on watchman.stanford.edu ft2YY
##########################################################################################

# 0 change password to Killifish, setup internet wifi
#sudo passwd root
#sudo passwd pi
#sudo apt-get update
#sudo apt-get install git -y
#git clone https://github.com/amckay1/KilliFeederSoftware.git

# 1 pull required software
apt-get update
apt-get install libpng-dev unzip wget libarchive-dev libtool m4 tmux automake squashfs-tools build-essential clang cmake gfortran -y
apt-get install vim python-pip python3-pip -y
pip3 install paho-mqtt
apt-get install mosquitto mosquitto-clients -y

# 2 mkdirs
mkdir $HOME/.KilliFeeder
mkdir $HOME/.KilliFeeder/data
mkdir $HOME/.KilliFeeder/updates
mkdir $HOME/.KilliFeeder/config
cp config/config $HOME/.KilliFeeder/config
cp ../Feeder/micropythoncode/main.py $HOME/.KilliFeeder/updates/

# 3 install Julia
wget https://julialang-s3.julialang.org/bin/linux/armv7l/1.0/julia-1.0.5-linux-armv7l.tar.gz
tar -xzf julia-1.0.5-linux-armv7l.tar.gz
rm julia-1.0.5-linux-armv7l.tar.gz
mv julia-1.0.5 $HOME
ln -s $HOME/julia-1.0.5/bin/julia /usr/local/bin/julia

# 4 setup email function
apt-get install ssmtp
mv /etc/ssmtp/ssmtp.conf /etc/ssmtp/ssmtp.conf.bak
cp $HOME/KilliFeeder/Software/RemoteServer/config/ssmtp.conf /etc/ssmtp/ssmtp.conf

# 5 install Julia from source
#git clone git://github.com/JuliaLang/julia.git
#cd julia
#make -j 4
#sudo ln -s /home/pi/julia/julia /usr/local/bin/julia
# Install KilliFeeder
#julia -e 'using Pkg; Pkg.add("http://github.com/amckay1/KilliFeeder.jl")'



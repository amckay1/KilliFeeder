#!/bin/bash

mkdir $HOME/.KilliFeeder
mkdir $HOME/.KilliFeeder/data
mkdir $HOME/.KilliFeeder/config
mkdir $HOME/.KilliFeeder/updates
cp ../config/config.toml $HOME/.KilliFeeder/config
cp ../../Feeder/micropythoncode/main.py $HOME/.KilliFeeder/updates/

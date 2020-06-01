# KilliFeeder Software

The software needed to setup feeders, servers, and watchman.
* Feeders: the devices that network with the Server directly.
* Local Server: the RPi3 + modem local hub for feeders to check in with.
* Remote Server: the AWS instance with defined path that the Local Server bridges its MQTT broker with.

### Required software:
* Linux machine, ideally running Ubuntu
* Julia language
* The "KilliFeeder.jl" package
* esptool.py: `pip install esptool`
    * https://github.com/espressif/esptool
* mpfshell:
    * git clone https://github.com/PMunch/mpfshell
    * cd mpfshell
    * sudo pip3 install .
* qr codes: sudo apt-get install python3-qrcode

### Before you begin:
* Know which port you will be using: before plugging in the Wemos D1 mini by usb, note the ports that appear when you list using devices with the wildcard `ls /dev/tty*`. Then plug in your device and look for those devices again. The difference is your port. For example, it is often "/dev/ttyUSB0"
* change the ownership for /dev/ttyUSB0 using `sudo chown user:user /dev/ttyUSB0`
* Configure your KilliFeeder package by tweaking the values found in KilliFeeder/config/config.toml including the port found above.

## Suggested order of setup:

### Feeders
* Attach Wemos D1 mini via USB and enter mpfshell, repeating the following for each feeder:
    1. open ttyUSB0
    2. lcd $HOME/KilliFeeder/Software/Feeder/micropythoncode
    3. put main.py
    4. put stepper_fxns.mpy
    5. import machine
    6. ci = ubinascii.hexlify(machine.unique_id()).decode("utf-8")
    7. print(ci)
        * Note down this value, it is the hexadecimal id value of the feeder
    * NOTE: if you'd like to change the stepper_fxns.py file, you need to install mpy-cross via `pip3 install mpy-cross`

### Local Server
NOTE: need to create shell script for this
modify pulldb for private key movement (watchman.pem)
can remove some of the utils in the Server/utils folder

1. Flash MicroSD card for Raspian to setup Raspberry Pi 3
* Use the Raspberry Pi foundation imager to install Raspbian Jessie on the RPi3 to install Raspbian 32bit onto a 8GB+ microsd card: https://www.raspberrypi.org/downloads/
* Navigate to /boot/config.txt in the newly flashed microsd card and add  "enable_uart=1" to end of file
2. Boot up RPi3 Local Server with newly flashed microsd card
* Log in (default username/password is "pi" "raspberry") and reset password to "pi" "Killifish" using `sudo passwd`
* Connect to the local wifi and clone using git the KilliFeeder.jl repo: `git clone https://github.com/amckay1/KilliFeeder` 
3. Setup daemons
* Enter `KilliFeeder/Software/LocalServer/setup_scripts` and run:
    *   `sudo bash server_setup.sh`
    *   `bash configure.sh`
    *   `sudo bash setup_daemons.sh`
* Check pub.service is working by entering `mosquitto_sub -t time` and receiving seconds from midnight iteratively

# Setup Netgear router
* Log in to your router (example for tplink router: "http://tplinkwifi.net")
* Login is printed on bottom of router "admin" and usual pi3 login passwd
    * Setup as an "Access Point" 
    * set wlan info to Pi3-AP, raspberry, and the ip address of the router to 192.168.0.1
    * set IP address to 192.168.0.13 for rpi3 (mac address needed)
* Connect the Local Server to the wifi router via ethernet
* Ensure the Local Server is using the wifi for ethernet and the wifi router for communicating with the feeders by reprioritizing:
    * `sudo apt-get install ifmetric`
    * `route -n` (note the metric that eth0 has and choose a lower value for wlan0, 50 is often low enough)
    * `sudo ifmetric wlan0 50`

### Setup Remote Server
1. Enter AWS and register domain via Route53: currently the github is configured for "www.killifeeder.com"
2. Launch a t2.medium EC2 ubuntu instance and download private keys
    * Sync private key to Local Server for access to EC2 instance via pulldb.service
    * ssh into server specifying private key `ssh -i "$HOME/.ssh/killifeeder.pem" ubuntu@[public address]`
3. Clone KilliFeeder onto Remote Server via `git clone https://github.com/amckay1/KilliFeeder` then run `KilliFeeder/Software/RemoteServer/RemoteServer_setup.sh` as root.
4. In same directory, run `sudo bash setup_daemons.sh`
	* ensure AWS is allowing TCP traffic on port 8883
	* Use script t.sh to make files "my-ca.crt server.crt server.key" then copy them in the directories as specified following:
	    * NOTE: the second common name (CN) needs to be the same as the domain you will be linking to, for example "www.killifeeder.com"
	    * need to be using config file (mosquitto.conf) with correct paths for certificates:
	    ```
	    port 8883
	    cafile /etc/mosquitto/ca_certificates/ca.crt
	    certfile /etc/mosquitto/certs/server.crt
	    keyfile /etc/mosquitto/certs/server.key

	    ```
	* Restart mosquitto service

After mosquitto is restarted, start sub:
`mosquitto_sub --cafile /etc/mosquitto/ca_certificates/ca.crt -h www.killifeeder.com -t test -p 8883`
And opening another tmux windown, try to send message:
`mosquitto_pub --cafile /etc/mosquitto/ca_certificates/ca.crt -h www.killifeeder.com -t test -m test -p 8883`

5. rsync "ca.crt" certificate to Local Server and place in ~/.KilliFeeder/config/

## Setting up MQTT on Local Server
* Add this to /etc/mosquitto/mosquitto.conf then restart mosquitto:
```
connection bridge-01
address www.killifeeder.com:8883
bridge_cafile /home/pi/.KilliFeeder/config/ca.crt
bridge_insecure false

topic # out 0
topic # in 0
```

* restart mosquitto and test with this:

`mosquitto_pub -t test -m testfromlocalserver`

* should show up on broker/www.killifeeder.com server

## Controlling the feeders

After powering on the feeders they should connect to the wifi router and look for instructions. Because the system is naive to new feeders their orders will not be immediately available and you will likely need to reset the feeders after a couple seconds. If connnected to mpfshell's repl you can watch this happen. Once connected and accounted for in the database, the feeder will pull down default orders (feeding 4 times a day) and begin calibrating (add food to the hopper before this
happens).

Once connected feeders can be controlled by using the KilliFeeder.jl package (https://github.com/amckay1/KilliFeeder.jl). The primary uses are to change feedings and to set calibration. For example, a typical session on the Remote Server where orders are changed using the feeder ID hexadecimal found in the flashing step above would entail changing the feeding times for feeder "d5624700" to seven evenly spaced feedings per day following calibration at the next opportunity.

`using KilliFeeder

id = "d5624700"
scheme = "7times"

KilliFeeder.send_delta_order(id, scheme)

KilliFeeder.send_cal_msg(id)`











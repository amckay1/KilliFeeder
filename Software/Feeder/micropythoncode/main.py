### recently updated with micropython 1.9.3
from umqtt.simple import MQTTClient
from stepper_fxns import step_rev, calibrate, feed, check_debug, prefeed, findnextfeed, createfeedingfromorders
import os
import machine
import time
import network
import ubinascii

main_v = "1.0"
print(main_v)

# a value between 0 and 65025 (in milliseconds, so 0 to 65 seconds)
rsalt = int.from_bytes(uos.urandom(2), 'int')

debug_mode = check_debug()

## conditioning LED = G14
lcond = machine.Pin(14, machine.Pin.OUT) # pulls down?

## sensor activation and LED = G12
tsens = machine.Pin(12, machine.Pin.OUT)
### turn everything off
tsens.off()
lcond.off()

## setup analog pin
adc = machine.ADC(0)
# configure RTC.ALARM0 to be able to wake the device
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
SERVER = "192.168.0.13"  ## the Pi3-AP
CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode("utf-8")

wlan = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
if ap_if.active():
    ap_if.active(False)

wlan.active(True)

def sub_cb(topic, msg):
    topicOI = str("orders/"+ CLIENT_ID)  ### might be str+bytes
    topic = topic.decode("utf-8")
    print(topic)
    if topic == "time":
        print("time topic")
        global ttime
        ttime = int(msg.decode("utf-8"))
        print(ttime)
        strtosend = CLIENT_ID + "," + str("5.0") + "," + str(ttime)
        c.publish(b"ctime", strtosend)
    if topic == topicOI:
        global orders
        orders = msg.decode("utf-8")
        print(orders)
    if topic == "status":
        if msg.decode("utf-8") == "updatetime":
            time.sleep(1)
            c.connect(clean_session=True)
            c.subscribe(b"update")
            time.sleep(1)
            print("checking for message")
            gc.collect()
            c.check_msg()

    if topic == "update":
        print(topic)
        print(msg)
        gc.collect()
        with open('main.py', 'wb') as fd:
            fd.write(msg)
        print("Updated main.py, resetting")
        machine.reset()
        time.sleep(3)

### setup MQTT
c = MQTTClient(CLIENT_ID, SERVER)
c.set_callback(sub_cb)

### setup the network:
print('connecting to network...')
wlan.connect('Pi3-AP', 'raspberry')
while not wlan.isconnected():
    machine.idle()

print(wlan.ifconfig())
# ubinascii.hexlify(wlan.ifconfig('mac'), ':')

print(machine.reset_cause())
if (machine.reset_cause() == machine.HARD_RESET) | (machine.reset_cause() == 5):
    print("Hard reset detected, checking for update")
    c.connect(clean_session=True)
    c.subscribe(b"status")
    time.sleep(1)
    print("checking for message")
    c.check_msg()

# Setup time, global time variables, and check time
global ttime
calibrated = "no"
ttime = 90000
# How long will the unit deep sleep after feeding?
postfeedsleepms = 60000 + rsalt# min * sec * ms_sec; 60*60*1000 = an hour, 300000 == 5 min, 60000 == 1 min


# Get the time #
timeouti = 0
while ttime == (90000):
    try:
        c.connect(clean_session=True)
        c.subscribe(b"time")
        while ttime == (60*1500):
            timeouti += 1
            c.check_msg()
            time.sleep(1)
            print(timeouti)
            if timeouti == 20:
                print("can't connect to server, deep sleeping for 5 min and will try again")
                deepsleeptime = 300000 + rsalt
                rtc.alarm(rtc.ALARM0, deepsleeptime)
                machine.deepsleep()
    except OSError as e:
        print("check_msg:", e)
        print("try to reconnect")
        print("deepsleep for 60 sec and retry")
        deepsleeptime = 60000 + rsalt
        rtc.alarm(rtc.ALARM0, deepsleeptime)
        machine.deepsleep()



print("ttime = ", ttime)

## first, check if file exists:
try:
    print("Looking for file")
    f = open('holdover.txt', 'r') #  f.write( strtosend)
    print("Found file, reading and trying to send")
    ## split between topic and message
    strtosend = f.read()
    try:
        c.publish(b"cfeed", strtosend)
    except OSError as e:
        print("can't publish, deep sleeping for 1 min and will try again")
        rtc.alarm(rtc.ALARM0, 60000)
        machine.deepsleep()
    f.close()
    os.remove('holdover.txt')
except OSError as e:
    print('no file, continuing')


orders = str()
### need to clean this up:
while orders == '':
    print("New orders being retrieved")
    c.connect(clean_session=True)
    orderstr = str("orders/" + CLIENT_ID)
    print(orderstr)
    c.subscribe(orderstr)
    while orders == '':
        c.check_msg()
        time.sleep(1)

# create feeding times array from orders
feedingtimes, calibrated= createfeedingfromorders(orders)

global nextfeed

### if calibration flag = 0, calibrate
if calibrated == "no":
    sensdiff, calmsg, calibrated = calibrate(adc, tsens,CLIENT_ID)  ### will later send this back to the server
    print("trying to publish calibration")
    print(calmsg)
    c.publish(b"calibrate", calmsg)
    time.sleep_ms(3000)
    print("should be sent")

## Now that we have our ttime, marching orders, and calibration, we can check these and feed:
need2feed = False
while ttime != (90000) and debug_mode:
    try:
        f = open("need2feed", "r")
        need2feed = True
        f.close()
    except:
        need2feed = False

    if need2feed:
        os.remove("need2feed")
        prefeed(lcond, c, ttime, calibrated, adc, tsens, CLIENT_ID, rsalt, rtc, postfeedsleepms)

    nextfeed = findnextfeed(ttime, feedingtimes)

    # put into deep sleep for 90% time to feeder (all in seconds)
    print("Next feeding is")
    print(nextfeed)
    if (nextfeed) > (120):
        sleepfor = int(nextfeed*0.8*(1000))
        print("Deep sleeping for:")
        print((sleepfor/1000))
        rtc.alarm(rtc.ALARM0, sleepfor)
        machine.deepsleep() ### uncomment in real deal

    if (120) >= (nextfeed) > 0:
        sleepfor = int(nextfeed*(1000))
        print("Deep sleeping briefly for:")
        print(nextfeed)
        f = open("need2feed", "w")
        f.close()
        rtc.alarm(rtc.ALARM0, sleepfor)
        machine.deepsleep()

print("in debug mode")

### where speed = ms pause, and ideal being step_for(100,1)
import time
import machine
import ubinascii
from umqtt.simple import MQTTClient

motor_pins = [13, 4, 15, 5]
motor_pins = [machine.Pin(pin, machine.Pin.OUT) for pin in motor_pins]
for pin in motor_pins:
    pin.off()

def step_rev(steps, speed):
    on_steps =  [0,1,1,2,2,3,3,0]
    off_steps = [3,3,0,0,1,1,2,2]
    for pin in motor_pins:
        pin.off()
    i = 0

    for s in range(steps):
        motor_pins[off_steps[i]].off()
        #print(motor_pins[off_steps[i]], "off")
        motor_pins[on_steps[i]].on()
        #print(motor_pins[on_steps[i]], "on")
        i = (i+1)%8
        time.sleep_ms(speed)

    for pin in motor_pins:
        pin.off()

def step_for(steps, speed):
    on_steps =  [0,3,3,2,2,1,1,0]# reverse of [0,1,1,2,2,3,3,0]
    off_steps = [1,1,0,0,3,3,2,2]# reverse of [3,3,0,0,1,1,2,2]
    for pin in motor_pins:
        pin.off()
    i = 0
    for _ in range(steps):
        motor_pins[off_steps[i]].off()
        #print(motor_pins[off_steps[i]], "off")
        motor_pins[on_steps[i]].on()
        #print(motor_pins[on_steps[i]], "on")
        i = (i+1)%8
        time.sleep_ms(speed)
    for pin in motor_pins:
        pin.off()


#cal_step_for(100, 5, adc, tsens) cal_step_for(2000, 5, adc, tsens)
def cal_step_for(steps, speed, adc, tsens):
    tsens.value(1)
    time.sleep_ms(500)
    on_steps =  [0,3,3,2,2,1,1,0]# reverse of [0,1,1,2,2,3,3,0]
    off_steps = [1,1,0,0,3,3,2,2]# reverse of [3,3,0,0,1,1,2,2]
    for pin in motor_pins:
        pin.off()
    # here, we really just want the extrema, min and max
    val = 0
    minval = 1024
    maxval = 0
    i = 0
    for s in range(steps):
        motor_pins[off_steps[i]].off()
        #print(motor_pins[off_steps[i]], "off")
        motor_pins[on_steps[i]].on()
        #print(motor_pins[on_steps[i]], "on")
        i = (i+1)%8
        val = adc.read()
        print(val)
        if val < minval:
            minval = val
        elif val > maxval:
            maxval = val

        time.sleep_ms(speed)
    for pin in motor_pins:
        pin.off()
    time.sleep_ms(500)
    tsens.value(0)
    return minval, maxval


#cal_step_for(100, 5, adc, tsens) cal_step_for(2000, 5, adc, tsens)
def cal_step_rev(steps, speed, adc, tsens):
    tsens.value(1)
    time.sleep_ms(500)
    on_steps =  [0,1,1,2,2,3,3,0]
    off_steps = [3,3,0,0,1,1,2,2]
    for pin in motor_pins:
        pin.off()
    val = 0
    minval = 1024
    maxval = 0
    i = 0
    for s in range(steps):
        motor_pins[off_steps[i]].off()
        #print(motor_pins[off_steps[i]], "off")
        motor_pins[on_steps[i]].on()
        #print(motor_pins[on_steps[i]], "on")
        i = (i+1)%8
        val = adc.read()
        print(val)
        if val < minval:
            minval = val
        elif val > maxval:
            maxval = val

        time.sleep_ms(speed)
    for pin in motor_pins:
        pin.off()
    time.sleep_ms(500)
    tsens.value(0)
    return minval, maxval

def seek_cal_step_for(steps, speed, adc, tsens, threshold):
    tsens.value(1)
    time.sleep_ms(500)
    on_steps =  [0,3,3,2,2,1,1,0]# reverse of [0,1,1,2,2,3,3,0]
    off_steps = [1,1,0,0,3,3,2,2]# reverse of [3,3,0,0,1,1,2,2]
    for pin in motor_pins:
        pin.off()
    # here, we really just want the extrema, min and max
    val = 0
    minval = 1024
    maxval = 0
    i = 0
    for s in range(steps):
        motor_pins[off_steps[i]].off()
        #print(motor_pins[off_steps[i]], "off")
        motor_pins[on_steps[i]].on()
        #print(motor_pins[on_steps[i]], "on")
        i = (i+1)%8
        val = adc.read()
        print(val)
        if val < threshold:
            time.sleep_ms(500)
            tsens.value(0)
            step_rev(700,5)
            return

        time.sleep_ms(speed)
    for pin in motor_pins:
        pin.off()
    time.sleep_ms(500)
    tsens.value(0)
    print("Did not find value less than threshold")
    return



### Need to rework this for stepper motor
#calibrate()
def calibrate(adc, tsens,CLIENT_ID):
    minvalu = 1025
    maxvalu = 1
    minstep = 0
    fineminstep = 0
    # first, get extrema
    min_val, max_val = cal_step_for(8000, 5, adc, tsens) # cal_step_for(800, 5, adc, tsens)
    print("max_val")
    print(max_val)
    print("min_val")
    print(min_val)
    threshold = (max_val - ((max_val - min_val)/2))
    print("treshold")
    print(threshold)

    # then, use to find region
    seek_cal_step_for(8000, 5, adc, tsens, threshold)
    # found the spot within ~100 steps
    sensdiff = max_val - min_val
    print("sensdiff")
    print(sensdiff)
    calmsg = str(CLIENT_ID + ",yes,"+str(sensdiff))
    calibrated = "yes"
    return sensdiff, calmsg, calibrated

                # maybe insert checkpoint here, a "calibrated = yes" if was able to reset
    #### get diff of values max and min, the mean, and ID lowest value for middle pt


### function for running servo and feeding, as well as checking for measurement
def feed(ttime,calibrated, adc, tsens, CLIENT_ID):
    min_val_out, max_val_out = cal_step_for(1400, 4, adc,tsens)
    print("Measure outbound: ", min_val_out)

    ### returning to measure point
    min_val_back, max_val_back = cal_step_rev(1400, 4, adc,tsens) # cal_step_rev(1300, 5, motor_pins, cond_adc,tsens) cal_step_rev(500, 5, motor_pins, cond_adc,tsens) cal_step_rev(100, 5, motor_pins, cond_adc,tsens)
    print("Measure return: ", min_val_back)

    ### Confirm that the unit fed: ttime, food going out measurement, "food" coming back in measurement
    strtosend = str(CLIENT_ID + "," + str(ttime) + ","+ str(min_val_out) + ","+ str(min_val_back)+","+(calibrated))
    print(strtosend)
    return(strtosend)

# check if debug mode:
def check_debug():
    debug_pin = machine.Pin(2, machine.Pin.IN) # pulls up, D4
    if debug_pin.value() < 0.5:
        print("entering debug mode")
        return False
    else:
        print("skipping debug mode")
        return True

# function for receiving message from server
def prefeed(lcond, c, ttime, calibrated, adc, tsens, CLIENT_ID, rsalt, rtc, postfeedsleepms):
    ### turn on led
    lcond.on()
    ### wait 3 seconds
    time.sleep(3)
    strtosend = feed((ttime),calibrated, adc, tsens, CLIENT_ID)
    lcond.off()
    print("publishing")
    try:
        c.publish(b"cfeed", strtosend)
    except OSError as e:
        print("Not able to pub, saving file then deepsleeping for 30 seconds")
        # need to write and save for later
        f = open("holdover.txt", 'w')
        f.write(strtosend)
        f.close()
        time.sleep(3)
        deepsleeptime = 30000 + rsalt
        rtc.alarm(rtc.ALARM0, deepsleeptime)
        machine.deepsleep()
    print("waiting")
    time.sleep(3)
    rtc.alarm(rtc.ALARM0, postfeedsleepms)
    print("Deep sleeping for postfeed")
    print(postfeedsleepms)
    machine.deepsleep()

def findnextfeed(ttime, feedingtimes):
    if max(x - ttime for x in feedingtimes)>=(0):
        return min(x - ttime for x in feedingtimes if (x-ttime)>=(0))
    else:
        return min(feedingtimes)+((86400)-ttime)   #next feeding plus remaining minutes in the day

def createfeedingfromorders(orders):
    print(orders)
    feedingtimes = orders.split(",")[0:-2]
    print(feedingtimes)
    calibrated = orders.split(",")[-2]
    #senspt = orders.split(",")[-1]
    print(calibrated)
    for i,feedtime in enumerate(feedingtimes):
        print(i, feedtime)
        feedingtimes[i] = int(feedtime)
    print(feedingtimes)
    return feedingtimes, calibrated



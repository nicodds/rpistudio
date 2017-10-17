import threading
import sys
import signal
import numpy as np
from time import sleep, gmtime, strftime
from peltier import *
#import sqlite3
from ABE_helpers import ABEHelpers
from ABE_ADCDifferentialPi import ADCDifferentialPi


# voltage-to-humitdy conversion parameters
alpha  = 0.0062
beta   = 0.16
alphaT = 0.00216
betaT  = 1.0546
vin    = 4.98
temp   = 30.0
# voltage conversion factor on the humidity sensor
f      = (159.47+8.998)/8.998
# channel on the adc
chT    = 1
chH    = 2
# gpio pins for polarity control
R_PWM=26
L_PWM=19
# polarity controller (used for temperature manipulation)
tctrl = Peltier(R_PWM, L_PWM)

ev = threading.Event()
ev.set()


# = = = = = = = = = = = = = = = NOTES = = = = = = = = = = = = = = =
#
# make a measure function that takes as input a dictionary with all
# the info needed to perform all measures and perform them on a single
# cycle, taking care of locking or any other requirement



def cleanup_pi(signal, frame):
    print("CTRL+C pressed, exiting...")
    tctrl.stop()
    tctrl.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_pi)

# function to convert an output voltage to relative humidity
def humidity_converter(v, T):
    rh_sensor = (v-beta*vin)/(alpha*vin)
    rh_true   = rh_sensor/(betaT-alphaT*T)
    return rh_true

# setup the ADC
i2c_helper = ABEHelpers()
bus        = i2c_helper.get_smbus()
adc        = ADCDifferentialPi(bus, 0x68, 0x69, 16)

def measure_ambient(sleep_seconds, evt):
    # setup the connection to the db
#    conn = sqlite3.connect('prova.db')
#    c    = conn.cursor()

    while True:
        measuresH  = np.ndarray(10)
        measuresT  = np.ndarray(10)
        evt.wait()
        evt.clear()
        for i in range(0, 10):
            measuresT[i] = adc.read_voltage(chT)*100
            read = adc.read_voltage(chH)
            measuresH[i] = humidity_converter(f*read, measuresT[i])
            sleep(0.1)
        evt.set()
        curtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print("%s --- Temperature: %f +/- %f --- Relative Humidity: %f +/- %f" % (curtime, measuresT.mean(), measuresT.std(), measuresH.mean(), measuresH.std()),)
#      c.execute("INSERT INTO humidity VALUES(?, ?, ?)", (curtime, measuresH.mean(), measuresH.std()))
 #       conn.commit()
        sleep(sleep_seconds)
        

def control_temperature(evt):
    curr_temp = 0.0
    
    while True:
#        if tctrl.time_in_status() > 6.0:
#            tctrl.stop()
#            sys.exit(0)
        
        # reinizialize the np array where measure samples get stored
        tmpt = np.ndarray(10)
        # wait until adc is available for measurements
        evt.wait()
        # inform other threads that we are using adc's channel
        evt.clear()
        
        for i in range(0, 10):
            tmpt[i] = adc.read_voltage(chT)*100
#            print(">>>>> ctrl --- %f" %(tmpt[i]))
            sleep(0.1)

        #inform other threads that adc's channel is free
        evt.set()
        # at this stage, curr_temp still holds the old value, so we
        # use it to compute the temperature variation across a cycle
        curr_temp = tmpt.mean()
        
        print(">>>>> In the control cycle... temperature %f" %(curr_temp))
        status = tctrl.get_status()
        max_relative_delta = 0.06
        max_absolute_delta = 0.09
        

        if status == HEATING:
        # if it is heating, let it heat until opportune
            if curr_temp >= temp+max_relative_delta:
                tctrl.stop()
                print("Stopping Peltier module after heating")
        elif status == COOLING:
        # if it is cooling, let it cools until opportune
            if curr_temp <= temp-max_relative_delta:
                tctrl.stop()
                print("Stopping Peltier module after cooling")
        elif status == STOPPED:
        # if it is stopped
            if curr_temp <= temp-max_absolute_delta:
            # start heating if temperature is too low
                tctrl.start_heatup()
                print("Too cold! Heating up...")
            elif curr_temp >= temp+max_absolute_delta:
            # start cooling if temperature is too high
                print("Too hot! Cooling down...")
                tctrl.start_cooldown()

        sleep(1)
        
        

def noise(sleep_seconds):
    while True:
        print('--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--')
        sleep(sleep_seconds)

w_sec = 30

t1 = threading.Thread(target=measure_ambient, args=(w_sec, ev,))
t2 = threading.Thread(target=control_temperature, args=(ev,))

t1.start()
t2.start()

    


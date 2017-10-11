import threading
import sys
import signal
import numpy as np
import time
from peltier import Peltier
#import sqlite3
from ABE_helpers import ABEHelpers
from ABE_ADCDifferentialPi import ADCDifferentialPi

#from ADCDifferentialPi import ABE_ADCDifferentialPi


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
            time.sleep(0.1)
        evt.set()
        curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print("%s --- Temperature: %f +/- %f --- Relative Humidity: %f +/- %f" % (curtime, measuresT.mean(), measuresT.std(), measuresH.mean(), measuresH.std()),)
#      c.execute("INSERT INTO humidity VALUES(?, ?, ?)", (curtime, measuresH.mean(), measuresH.std()))
 #       conn.commit()
        time.sleep(sleep_seconds)

def control_temperature(evt):
    last_temp = 0.0
    curr_temp = 0.0
    delta_t
    
    while True:
        # at the beginning of the while block "curr_temp" represent
        # the last measured temperature
        last_temp = curr_temp
        # reinizialize the np array where measure samples get stored
        tmpt = np.ndarray(10)
        # wait until adc is available for measurements
        evt.wait()
        # inform the other threads that we are using adc's channel
        evt.clear()
        
        for i in range(0, 10):
            tmpt[i] = adc.read_voltage(chT)*100
#            print(">>>>> ctrl --- %f" %(tmpt[i]))
            time.sleep(0.1)
        evt.set()
        curr_temp = tmpt.mean()
        print(">>>>> In the control cycle... temperature %f" %(tmpt.mean()))
        if curr_temp >= 30.09:
            if (
            if tctrl.get_status() != 2:
                print("Too hot! Cooling down...")
                tctrl.start_cooldown()
        elif tmpt.mean() <= 29.91:
            if tctrl.get_status() != 1:
                print("Too cold! Heating up...")
                tctrl.start_heatup()
        else:
            if tctrl.get_status() != 0:
                print("Stopping Peltier module")
                tctrl.stop()

        time.sleep(4)
        
        

def noise(sleep_seconds):
    while True:
        print('--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--')
        time.sleep(sleep_seconds)

w_sec = 30

t1 = threading.Thread(target=measure_ambient, args=(w_sec, ev,))
t2 = threading.Thread(target=control_temperature, args=(ev,))

t1.start()
t2.start()

    


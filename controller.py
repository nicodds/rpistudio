import threading
import sys
import signal
import numpy as np
from time import sleep, gmtime, strftime
from peltier import *
import sqlite3
from ABE_helpers import ABEHelpers
from ABE_ADCDifferentialPi import ADCDifferentialPi
import SDL_Pi_HDC1000



temp = 30.007
# channels on the adc
chTctrl = 1
chTmeas = 6
chPMT1  = 5
chPMT2  = 7
# gpio pins for polarity control
H_PWM=26
C_PWM=19
# polarity controller (used for temperature manipulation)
temperature_ctrl   = Peltier(C_PWM, H_PWM, 4.1, 2.5, 3.5)
# setup the i2c sensor
hdc1080 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
# setup the ADC
i2c_helper = ABEHelpers()
bus        = i2c_helper.get_smbus()
adc        = ADCDifferentialPi(bus, 0x68, 0x69, 16)


# = = = = = = = = = = = = = = = NOTES = = = = = = = = = = = = = = =
#
# make a measure function that takes as input a dictionary with all
# the info needed to perform all measures and perform them on a single
# cycle, taking care of locking or any other requirement

# convert measure of PMT on channel 5
def convert_PMT1(measures):
    factor   = 12.735170
    fact_err =  0.034583

    measure = measures.mean()
    error   = measures.std()
    true_measure = factor * measure
    true_error   = measure*fact_err + factor * error

    return (true_measure, true_error)

# convert measure of PMT on channel 7
def convert_PMT2(measures):
    factor   = 12.694516
    fact_err =  0.033417

    measure = measures.mean()
    error   = measures.std()    
    true_measure = factor * measure
    true_error   = measure*fact_err + factor * error

    return (true_measure, true_error)


def calibrated_temperature(voltages):
    intercept = 3.62227975e-02
    pendence  = 9.11017050e+01
    si, sp    = 0.01999287, 0.06932112

    value  = intercept + voltages.mean()*pendence
    sd_err = si + voltages.std()*pendence + sp*voltages.mean()

    return (value, sd_err)

def cleanup_pi(signal, fname):
    print("CTRL+C pressed, exiting...")
    t1.is_running = False
    t2.is_running = False
    temperature_ctrl.stop()
    temperature_ctrl.cleanup()
    sleep(0.5)
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_pi)




def measure_ambient(sleep_seconds):
    # The exit from the thread running this function could be difficult
    # due to the potentially long running sleep at the end of this
    # function. A better exit strategy should be found
    #
    # setup the connection to the db
    conn = sqlite3.connect('prova.db')
    c    = conn.cursor()
    t    = threading.currentThread()
    formatted_string = """------- %s -------
Temperature: \t%2.5f +/- %2.5f 
Humidity: \t%2.5f +/- %2.5f
Photo mult1: \t%2.5f +/- %2.5f
Photo mult2: \t%2.5f +/- %2.5f
------------------------------------"""
    
    start_time   = time()
    last_measure = 0
    measures     = {'humidity': None, 'temperature': None, 'pmt1': None, 'pmt2': None}
    repetitions  = 15

    while t.is_running:
        secs_since_measure = time() - last_measure

        if secs_since_measure >= sleep_seconds:
            secs_spent = int(time() - start_time)
            last_measure = time()
            
            for k in measures.keys():
                measures[k]  = np.ndarray(repetitions)
        
            for i in range(0, repetitions):
                for k in measures.keys():
                    if k == 'temperature':
                        measures[k][i] = adc.read_voltage(chTmeas)
                    elif k == 'humidity':
                        measures[k][i] = hdc1080.readHumidity()
                    elif k == 'pmt1':
                        measures[k][i] = adc.read_voltage(chPMT1)
                    elif k == 'pmt2':
                        measures[k][i] = adc.read_voltage(chPMT2)
            

            curtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
            print(formatted_string %(curtime, *calibrated_temperature(measures['temperature']),
                                 measures['humidity'].mean(), measures['humidity'].std(),
                                 *convert_PMT1(measures['pmt1']),
                                 *convert_PMT2(measures['pmt2'])))

            c.execute("INSERT INTO experiment VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (secs_spent, *calibrated_temperature(measures['temperature']),
                  measures['humidity'].mean(), measures['humidity'].std(),
                  *convert_PMT1(measures['pmt1']),
                  *convert_PMT2(measures['pmt2'])))
            conn.commit()
        #sleep(sleep_seconds)

                

def control_temperature(sleep_seconds):
    curr_temp    = 0.0
    start_time   = time()
    t            = threading.currentThread()
    last_measure = 0
    
    while t.is_running:
        secs_since_measure = time() - last_measure

        if secs_since_measure >= sleep_seconds:
            last_measure = time()
            # reinizialize the np array where measure samples get stored
            tmp_temperature = np.ndarray(5)
        
            for i in range(0, 5):
                tmp_temperature[i] = adc.read_voltage(chTctrl)

            curr_temp = calibrated_temperature(tmp_temperature)
            pwm = temperature_ctrl.adjust(temp-curr_temp[0])
            print(">>>>> In the control thread: temperature %f (%f)" %(curr_temp))

#        sleep(sleep_seconds)

##########################################################################
# main
measure_wait_sec = 5
control_wait_sec = 1


print("Starting program...")
hdc1080.turnHeaterOn()
sleep(5)
hdc1080.turnHeaterOff()
hdc1080.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
hdc1080.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT)

t1 = threading.Thread(name='control',
                      target=measure_ambient,
                      args=(measure_wait_sec,))
t2 = threading.Thread(name='measure',
                      target=control_temperature,
                      args=(control_wait_sec,))

t1.is_running = True
t2.is_running = True

t1.start()
t2.start()


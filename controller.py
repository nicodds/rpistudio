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

def cleanup_pi(signal, frame):
    print("CTRL+C pressed, exiting...")
    temperature_ctrl.stop()
    temperature_ctrl.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_pi)




def measure_ambient(sleep_seconds):
    # setup the connection to the db
    conn = sqlite3.connect('prova.db')
    c    = conn.cursor()
    formatted_string = """--- %s ---
Temperature: \t%2.5f +/- %2.5f 
Humidity: \t%2.5f +/- %2.5f
Photo mult1: \t%2.5f +/- %2.5f
Photo mult2: \t%2.5f +/- %2.5f
Voltage: \t%2.5f"""
    
    start_time = time()
    measures    = {'humidity': None, 'temperature': None, 'pmt1': None, 'pmt2': None}
    repetitions = 15

    while True:
        secs_spent = int(time() - start_time)
        
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
            
            sleep(0.1)


        curtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        print(formatted_string %(curtime, *calibrated_temperature(measures['temperature']),
                                 measures['humidity'].mean(), measures['humidity'].std(),
                                 *convert_PMT1(measures['pmt1']),
                                 *convert_PMT2(measures['pmt2']),
                                 adc.read_voltage(8)))

        c.execute("INSERT INTO experiment VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (secs_spent, *calibrated_temperature(measures['temperature']),
                  measures['humidity'].mean(), measures['humidity'].std(),
                  *convert_PMT1(measures['pmt1']),
                  *convert_PMT2(measures['pmt2'])))
        conn.commit()
        sleep(sleep_seconds)

                

def control_temperature():
    curr_temp = 0.0
    start_time= time()
    
    while True:
        # reinizialize the np array where measure samples get stored
        tmp_temperature = np.ndarray(5)
        
        for i in range(0, 5):
            tmp_temperature[i] = adc.read_voltage(chTctrl)
            sleep(0.1)

        curr_temp = calibrated_temperature(tmp_temperature)
        pwm = temperature_ctrl.adjust(temp-curr_temp[0])
        print(">>>>> In the control cycle... temperature %f (%f)" %(curr_temp))

        sleep(1)

w_sec = 150

print("Starting program...")
hdc1080.turnHeaterOn()
sleep(5)
hdc1080.turnHeaterOff()
hdc1080.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
hdc1080.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT)

t1 = threading.Thread(target=measure_ambient, args=(w_sec,))
t2 = threading.Thread(target=control_temperature)

t1.start()
t2.start()


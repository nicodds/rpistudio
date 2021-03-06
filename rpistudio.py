# Copyright 2018 Domenico Delle Side <nico@delleside.org>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an "AS
#    IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#    express or implied.  See the License for the specific language
#    governing permissions and limitations under the License.

import threading
import sys
import signal
import numpy as np
import sqlite3
from time import time, sleep, gmtime, strftime
from controllers import Peltier
from sensors import (HumiditySensor,
                     TempControlSensor,
                     TempMeasureSensor,
                     Pmt1Sensor,
                     Pmt2Sensor)
#from plotly_graphs import update_graphs



temp = 30.015
# channels on the adc
chTctrl = 1
chTmeas = 6
chPMT1  = 5
chPMT2  = 8
# gpio pins for polarity control
HOT_PWM_GPIO  = 26
COLD_PWM_GPIO = 19
# polarity controller (used for temperature manipulation)
temperature_ctrl   = Peltier(cold_gpio = COLD_PWM_GPIO,
                             hot_gpio  = HOT_PWM_GPIO,
                             kp = 4.3,
                             ki = 3.5,
                             kd = 2.5)
# setup sensors
humidity_sensor  = HumiditySensor(address=0x40, name='rh')
temp_ctrl_sensor = TempControlSensor(channel=chTctrl, name='temp_control')
temp_meas_sensor = TempMeasureSensor(channel=chTmeas, name='temp')
pmt1_sensor      = Pmt1Sensor(channel=chPMT1, name='pmt1')
pmt2_sensor      = Pmt2Sensor(channel=chPMT2, name='pmt2')

sensors = [temp_meas_sensor, humidity_sensor, pmt1_sensor, pmt2_sensor]



def cleanup_pi(signal, fname):
    print("CTRL+C pressed, exiting...")
    t1.is_running = False
    t2.is_running = False
    temperature_ctrl.stop()
    temperature_ctrl.cleanup()
    t2.join()
    t1.join()
#    t3.cancel()

    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_pi)


def print_measures(measures):
    formatted_string = """------- %s -------
Temperature: \t%2.5f +/- %2.5f 
Humidity: \t%2.5f +/- %2.5f
Photo mult1: \t%2.5f +/- %2.5f
Photo mult2: \t%2.5f +/- %2.5f
-----------------------------------"""
    
    curtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
    print(formatted_string %(curtime, measures['temp'].mean(), measures['temp'].std(),
                             measures['rh'].mean(), measures['rh'].std(),
                             measures['pmt1'].mean(), measures['pmt1'].std(),
                             measures['pmt2'].mean(), measures['pmt2'].std()))
        


def measure_ambient(sleep_seconds):
    # The exit from the thread running this function could be difficult
    # due to the potentially long running sleep at the end of this
    # function. A better exit strategy should be found
    #
    # setup the connection to the db
    conn = sqlite3.connect('rpistudio.db')
    c    = conn.cursor()
    t    = threading.currentThread()
    start_time   = time()
    last_measure = 0
    measures     = {}
    repetitions  = 15

    while t.is_running:
        secs_since_measure = time() - last_measure

        if secs_since_measure < sleep_seconds:
            sleep(0.5)
            continue 

        
        secs_spent = int(time() - start_time)
        last_measure = time()
        
        for sensor in sensors:
            measures[sensor.get_name()]  = np.ndarray(repetitions)
        
        for i in range(0, repetitions):
            for sensor in sensors:
                measures[sensor.get_name()][i] = sensor.measure()

        print_measures(measures)

        c.execute("INSERT INTO experiment VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (secs_spent, measures['temp'].mean(), measures['temp'].std(),
                   measures['rh'].mean(), measures['rh'].std(),
                   measures['pmt1'].mean(), measures['pmt1'].std(),
                   measures['pmt2'].mean(), measures['pmt2'].std()))
        conn.commit()

                

def control_temperature(sleep_seconds):
    curr_temp    = 0.0
    t            = threading.currentThread()
    last_measure = 0
    
    while t.is_running:
        secs_since_measure = time() - last_measure

        if secs_since_measure >= sleep_seconds:
            last_measure = time()
            # reinizialize the np array where measure samples get stored
            tmp_temperature = np.ndarray(5)
        
            for i in range(0, 5):
                tmp_temperature[i] = temp_ctrl_sensor.measure()

            curr_temp = tmp_temperature.mean()
            pwm = temperature_ctrl.adjust(temp-curr_temp)
            print(">>>>> In the control thread: temperature %f (%f)" %(curr_temp, tmp_temperature.std()))


##########################################################################
# main
measure_wait_sec = 150
control_wait_sec = 0.7 


print("Starting program...")
humidity_sensor.prepare_sensor()

t1 = threading.Thread(name='control',
                      target=measure_ambient,
                      args=(measure_wait_sec,))
t2 = threading.Thread(name='measure',
                      target=control_temperature,
                      args=(control_wait_sec,))



#t1.daemon = True
#t2.daemon = True
t1.is_running = True
t2.is_running = True

t1.start()
t2.start()


#update_graphs(2000)
